"""Helpers for NMEA 2000 ."""

from __future__ import annotations
from dataclasses import dataclass
import time


def _u_le(b, i, size):
	return int.from_bytes(b[i:i+size], "little", signed=False)


def _s_le(b, i, size):
	return int.from_bytes(b[i:i+size], "little", signed=True)


class IdStore:
	def __init__(self):
		self._data = {}

	def set(self, id, value):
		self._data[id] = value

	def get(self, id):
		return self._data.get(id)

	def all(self):
		return self._data.copy()


class N2kFastPacketReassembler:
	def __init__(self, timeout_s=2.0, max_inflight=1024):
		self.buf = {}  # (pgn, src, dest, seq) -> state dict
		self.timeout_s = timeout_s
		self.max_inflight = max_inflight

	@staticmethod
	def _seq_and_frame(b0: int):
		return (b0 >> 5) & 0x07, b0 & 0x1F

	def _purge(self):
		now = time.monotonic()
		to_del = [k for k, st in self.buf.items() if now - st["ts"] > self.timeout_s]
		for k in to_del:
			del self.buf[k]
		if len(self.buf) > self.max_inflight:
			victims = sorted(self.buf.items(), key=lambda kv: kv[1]["ts"])
			for k, _ in victims[: len(self.buf) - self.max_inflight]:
				del self.buf[k]

	def feed(self, pgn: int, src: int, dest: int, data: bytes):
		self._purge()
		seq, frame = self._seq_and_frame(data[0])
		key = (pgn, src, dest, seq)
		now = time.monotonic()

		if frame == 0:
			total_len = data[1]
			payload = data[2:8]
			self.buf[key] = {
				"expected_len": total_len,
				"chunks": bytearray(payload),
				"next_frame": 1,
				"ts": now,
			}
			if len(payload) >= total_len:
				out = bytes(payload[:total_len])
				del self.buf[key]
				return out
			return None

		st = self.buf.get(key)
		if not st or st["next_frame"] != frame:
			return None

		st["chunks"].extend(data[1:8])
		st["next_frame"] += 1
		st["ts"] = now

		if len(st["chunks"]) >= st["expected_len"]:
			out = bytes(st["chunks"][: st["expected_len"]])
			del self.buf[key]
			return out
		return None


@dataclass
class DecodedFrame:
	can_id: int
	source_id: int
	pgn_id: int
	dest_id: int
	priority: int
	isoname: int | None
	payload: bytes | None


def _decode_frame(canid: int, data_bytes: bytes, reasm: N2kFastPacketReassembler):
	source_id, pgn_id, dest_id, priority = decodeCanId(canid)
	payload = decode_payload(reasm, pgn_id, source_id, dest_id, data_bytes)
	if pgn_id == 60928:
		print("aaaaa",flush=True)
		store.set(source_id, _u_le(payload, 0, 8))
		print("bbbbb",flush=True)
	return DecodedFrame(canid, source_id, pgn_id, dest_id, priority, store.get(source_id), payload)


def decodeBlueCtrlNativeCan(text: str, reasm: N2kFastPacketReassembler | None = None):
	parts = text.split(",")
	canid = int(parts[0], 16)
	data_bytes = bytes(int(x, 16) for x in parts[1:])
	if reasm is None:
		reasm = globals()["reasm"]
	return _decode_frame(canid, data_bytes, reasm)


def decodeYachtDevices(text: str, reasm: N2kFastPacketReassembler | None = None):
	text = text.strip()
	if text.startswith("Parse error:"):
		text = text[len("Parse error:") :].strip()

	parts = text.split(" ")
	canid = int(parts[2], 16)
	data_bytes = bytes(int(x, 16) for x in parts[3:])
	if reasm is None:
		reasm = globals()["reasm"]
	return _decode_frame(canid, data_bytes, reasm)


def decodeCanId(can_id: int):
	source_id = can_id & 0xFF
	pgn_id_raw = (can_id >> 8) & 0x3FFFF
	priority = (can_id >> 26) & 0x07

	dp = (pgn_id_raw >> 16) & 0x3
	pf = (pgn_id_raw >> 8) & 0xFF
	ps = pgn_id_raw & 0xFF
	if pf < 0xF0:
		dest_id = ps
		pgn_id = (dp << 16) | (pf << 8)
	else:
		dest_id = 255
		pgn_id = (dp << 16) | (pf << 8) | ps
	return source_id, pgn_id, dest_id, priority


FAST_PACKET_PGNS = {
	126208, 126464, 126720, 126983, 126984, 126985, 126986, 126987, 126988,
	126996, 126998, 127233, 127237, 127489, 127490, 127491, 127494, 127495,
	127496, 127497, 127498, 127503, 127504, 127506, 127507, 127509, 127510,
	127511, 127512, 127513, 127514, 128275, 128520, 128538, 129029, 129038,
	129039, 129040, 129041, 129044, 129045, 129284, 129285, 129301, 129302,
	129538, 129540, 129541, 129542, 129545, 129547, 129549, 129551, 129556,
	129792, 129793, 129794, 129795, 129796, 129797, 129798, 129799, 129800,
	129801, 129802, 129803, 129804, 129805, 129806, 129807, 129808, 129809,
	129810, 130052, 130053, 130054, 130060, 130061, 130064, 130065, 130066,
	130067, 130068, 130069, 130070, 130071, 130072, 130073, 130074, 130320,
	130321, 130322, 130323, 130324, 130330, 130561, 130562, 130563, 130564,
	130565, 130566, 130567, 130569, 130570, 130571, 130572, 130573, 130574,
	130577, 130578, 130580, 130581, 130583, 130584, 130586, 130816, 130817,
	130818, 130819, 130820, 130821, 130822, 130823, 130824, 130825, 130827,
	130828, 130831, 130832, 130833, 130834, 130835, 130836, 130837, 130838,
	130839, 130840, 130842, 130843, 130845, 130846, 130847, 130848, 130850,
	130851, 130856, 130860, 130880, 130881, 130918, 130944,
}


def decode_payload(reasm: N2kFastPacketReassembler, pgn_id: int, source_id: int, dest_id: int, data_bytes: bytes):
	if pgn_id in FAST_PACKET_PGNS:
		return reasm.feed(pgn_id, source_id, dest_id, data_bytes)
	return data_bytes


reasm = N2kFastPacketReassembler()
store = IdStore()

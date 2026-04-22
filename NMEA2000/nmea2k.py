"""Helpers for NMEA 2000 ."""

from __future__ import annotations
from dataclasses import dataclass
import time


def read_unsigned_le_bytes(buffer: bytes, byte_offset: int, byte_length: int):
	"""Read an unsigned little-endian integer from a byte-addressed field."""
	return int.from_bytes(buffer[byte_offset:byte_offset + byte_length], "little", signed=False)


def read_signed_le_bytes(buffer: bytes, byte_offset: int, byte_length: int):
	"""Read a signed little-endian integer from a byte-addressed field."""
	return int.from_bytes(buffer[byte_offset:byte_offset + byte_length], "little", signed=True)


def read_unsigned_le_bits(buffer: bytes, bit_offset: int, bit_length: int):
	"""Read an unsigned little-endian integer from a bit-addressed field.

	Bit offsets are counted from the payload LSB upward:
	`bit_offset == 0` is bit 0 of `buffer[0]`, `bit_offset == 8` is bit 0 of
	`buffer[1]`, and so on.
	"""
	if bit_length <= 0:
		raise ValueError("bit_length must be positive")
	start_byte = bit_offset // 8
	end_bit = bit_offset + bit_length
	end_byte = (end_bit + 7) // 8
	value = int.from_bytes(buffer[start_byte:end_byte], "little", signed=False)
	shift = bit_offset % 8
	return (value >> shift) & ((1 << bit_length) - 1)


def read_signed_le_bits(buffer: bytes, bit_offset: int, bit_length: int):
	"""Read a signed little-endian integer from a bit-addressed field.

	This uses the same bit numbering as `read_unsigned_le_bits()` and applies
	two's-complement sign extension over `bit_length`.
	"""
	unsigned_value = read_unsigned_le_bits(buffer, bit_offset, bit_length)
	sign_bit = 1 << (bit_length - 1)
	if unsigned_value & sign_bit:
		return unsigned_value - (1 << bit_length)
	return unsigned_value


# Backward-compatible helper aliases.
_read_unsigned_le_bytes = read_unsigned_le_bytes
_read_signed_le_bytes = read_signed_le_bytes
_read_unsigned_le_bits = read_unsigned_le_bits
_read_signed_le_bits = read_signed_le_bits


class IsoNameStore:
	def __init__(self):
		self._data = {}

	def set(self, source_id: int, iso_name: int):
		self._data[source_id] = iso_name

	def get(self, source_id: int):
		return self._data.get(source_id)

	def as_dict(self):
		return self._data.copy()


class ActivePgnSourceStore:
	def __init__(self, timeout_s: float = 600.0):
		self._data = {}  # (pgn_id, source_id) -> last_seen_monotonic
		self.timeout_s = timeout_s

	def _purge(self):
		now = time.monotonic()
		expired_keys = [
			key
			for key, last_seen in self._data.items()
			if now - last_seen > self.timeout_s
		]
		for key in expired_keys:
			del self._data[key]

	def touch(self, pgn_id: int, source_id: int):
		self._purge()
		self._data[(pgn_id, source_id)] = time.monotonic()

	def list_pairs(self):
		self._purge()
		return sorted(self._data.keys())

	def as_dict(self):
		self._purge()
		return self._data.copy()


class N2kFastPacketReassembler:
	def __init__(self, timeout_s=2.0, max_inflight=1024):
		self._inflight_packets = {}  # (pgn, src, dest, seq) -> state dict
		self.timeout_s = timeout_s
		self.max_inflight = max_inflight

	@staticmethod
	def _parse_sequence_and_frame(first_byte: int):
		return (first_byte >> 5) & 0x07, first_byte & 0x1F

	def _purge(self):
		now = time.monotonic()
		expired_keys = [
			key
			for key, packet_state in self._inflight_packets.items()
			if now - packet_state["ts"] > self.timeout_s
		]
		for key in expired_keys:
			del self._inflight_packets[key]
		if len(self._inflight_packets) > self.max_inflight:
			oldest_packets = sorted(
				self._inflight_packets.items(),
				key=lambda item: item[1]["ts"],
			)
			for key, _ in oldest_packets[: len(self._inflight_packets) - self.max_inflight]:
				del self._inflight_packets[key]

	def push_frame(self, pgn_id: int, source_id: int, destination_id: int, frame_data: bytes):
		self._purge()
		sequence_id, frame_index = self._parse_sequence_and_frame(frame_data[0])
		key = (pgn_id, source_id, destination_id, sequence_id)
		now = time.monotonic()

		if frame_index == 0:
			total_payload_length = frame_data[1]
			payload_bytes = frame_data[2:8]
			self._inflight_packets[key] = {
				"expected_len": total_payload_length,
				"chunks": bytearray(payload_bytes),
				"next_frame": 1,
				"ts": now,
			}
			if len(payload_bytes) >= total_payload_length:
				reassembled_payload = bytes(payload_bytes[:total_payload_length])
				del self._inflight_packets[key]
				return reassembled_payload
			return None

		packet_state = self._inflight_packets.get(key)
		if not packet_state or packet_state["next_frame"] != frame_index:
			return None

		packet_state["chunks"].extend(frame_data[1:8])
		packet_state["next_frame"] += 1
		packet_state["ts"] = now

		if len(packet_state["chunks"]) >= packet_state["expected_len"]:
			reassembled_payload = bytes(packet_state["chunks"][: packet_state["expected_len"]])
			del self._inflight_packets[key]
			return reassembled_payload
		return None

	def feed(self, pgn: int, src: int, dest: int, data: bytes):
		return self.push_frame(pgn, src, dest, data)


@dataclass
class DecodedFrame:
	can_id: int
	source_id: int
	pgn_id: int
	dest_id: int
	priority: int
	iso_name: int | None
	payload: bytes | None


def _decode_can_frame(can_id: int, data_bytes: bytes, reassembler: N2kFastPacketReassembler):
	source_id, pgn_id, dest_id, priority = decode_can_id(can_id)
	active_pgn_source_store.touch(pgn_id, source_id)
	payload = decode_n2k_payload(reassembler, pgn_id, source_id, dest_id, data_bytes)
	if pgn_id == 60928:
		iso_name_store.set(source_id, read_unsigned_le_bytes(payload, 0, 8))
	return DecodedFrame(can_id, source_id, pgn_id, dest_id, priority, iso_name_store.get(source_id), payload)


def decode_bluectrl_native_can(text: str, reassembler: N2kFastPacketReassembler | None = None):
	parts = text.split(",")
	can_id = int(parts[0], 16)
	data_bytes = bytes(int(x, 16) for x in parts[1:])
	if reassembler is None:
		reassembler = globals()["default_reassembler"]
	return _decode_can_frame(can_id, data_bytes, reassembler)


def decode_yacht_devices_message(text: str, reassembler: N2kFastPacketReassembler | None = None):
	text = text.strip()
	if text.startswith("Parse error:"):
		text = text[len("Parse error:") :].strip()

	parts = text.split(" ")
	can_id = int(parts[2], 16)
	data_bytes = bytes(int(x, 16) for x in parts[3:])
	if reassembler is None:
		reassembler = globals()["default_reassembler"]
	return _decode_can_frame(can_id, data_bytes, reassembler)


def decode_can_id(can_id: int):
	source_id = can_id & 0xFF
	raw_pgn_bits = (can_id >> 8) & 0x3FFFF
	priority = (can_id >> 26) & 0x07

	data_page = (raw_pgn_bits >> 16) & 0x3
	pdu_format = (raw_pgn_bits >> 8) & 0xFF
	pdu_specific = raw_pgn_bits & 0xFF
	if pdu_format < 0xF0:
		dest_id = pdu_specific
		pgn_id = (data_page << 16) | (pdu_format << 8)
	else:
		dest_id = 255
		pgn_id = (data_page << 16) | (pdu_format << 8) | pdu_specific
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


def decode_n2k_payload(
	reassembler: N2kFastPacketReassembler,
	pgn_id: int,
	source_id: int,
	dest_id: int,
	data_bytes: bytes,
):
	if pgn_id in FAST_PACKET_PGNS:
		return reassembler.push_frame(pgn_id, source_id, dest_id, data_bytes)
	return data_bytes


def decodeBlueCtrlNativeCan(text: str, reasm: N2kFastPacketReassembler | None = None):
	return decode_bluectrl_native_can(text, reasm)


def decodeYachtDevices(text: str, reasm: N2kFastPacketReassembler | None = None):
	return decode_yacht_devices_message(text, reasm)


def decodeCanId(can_id: int):
	return decode_can_id(can_id)


def decode_payload(reasm: N2kFastPacketReassembler, pgn_id: int, source_id: int, dest_id: int, data_bytes: bytes):
	return decode_n2k_payload(reasm, pgn_id, source_id, dest_id, data_bytes)


def list_active_pgn_source_pairs():
	return active_pgn_source_store.list_pairs()


def listActivePgnSourcePairs():
	return list_active_pgn_source_pairs()


default_reassembler = N2kFastPacketReassembler()
iso_name_store = IsoNameStore()
active_pgn_source_store = ActivePgnSourceStore()

# Backward-compatible module globals.
reasm = default_reassembler
store = iso_name_store
active_pairs_store = active_pgn_source_store

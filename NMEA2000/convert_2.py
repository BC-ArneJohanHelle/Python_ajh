import sys,time

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

	def delete(self, id):
		if id in self._data:
			del self._data[id]

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
		# Drop timed-out entries
		to_del = [k for k, st in self.buf.items() if now - st["ts"] > self.timeout_s]
		for k in to_del:
			del self.buf[k]
		# If still too many, drop oldest first (LRA)
		if len(self.buf) > self.max_inflight:
			victims = sorted(self.buf.items(), key=lambda kv: kv[1]["ts"])
			for k, _ in victims[:len(self.buf) - self.max_inflight]:
				del self.buf[k]

	def feed(self, pgn: int, src: int, dest:int, data: bytes):
		#if len(data) != 8:
			#print("Strange",pgn,list(data),flush=True)
			#raise ValueError("Expect 8 data bytes per CAN frame")

		self._purge()
		seq, frame = self._seq_and_frame(data[0])
		key = (pgn, src, dest, seq)
		now = time.monotonic()

		if frame == 0:
			total_len = data[1]
			payload = data[2:8]  # 6 bytes
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
			# Out of order / missing start: ignore this frame.
			return None

		st["chunks"].extend(data[1:8])   # 7 bytes
		st["next_frame"] += 1
		st["ts"] = now

		if len(st["chunks"]) >= st["expected_len"]:
			out = bytes(st["chunks"][:st["expected_len"]])
			del self.buf[key]
			return out
		return None
		


def decodeBlueCtrlNativeCan(Text:str):
	parts = Text.split(",")
	canid = (int(parts[0], 16))
	data_bytes = bytes(int(x, 16) for x in parts[1:])	

	return canid, data_bytes 

def decodeYachtDevices(Text: str):
	Text = Text.strip()
	if Text.startswith("Parse error:"):
		Text = Text[len("Parse error:"):].strip()

	parts = Text.split(" ")
	canid = (int(parts[2], 16))
	data_bytes = bytes(int(x, 16) for x in parts[3:])	
	return canid, data_bytes 

    
def decodeCanId(CanId:int):
	source_id = CanId & 0xFF             # bits 0-7 = 8 bits
	pgn_id_raw = (CanId >> 8) & 0x3FFFF  # bits 8-25 = 18 bits
	priority = (CanId >> 26) & 0x07      # bits 26-28 = 3 bits
	
	dp = (pgn_id_raw >> 16) & 0x3    # bits 16-17
	pf = (pgn_id_raw >> 8) & 0xFF    # bits 8-15
	ps = pgn_id_raw & 0xFF           # bits 0-7
	if pf < 0xF0:
		# PDU1 format: PS is destination address
		dest_id = ps
		pgn_id = (dp << 16) | (pf << 8)
	else:
		# PDU2 format: broadcast, destination is always 255
		dest_id = 255
		pgn_id = (dp << 16) | (pf << 8) | ps
	return source_id, pgn_id, dest_id, priority 

reasm = N2kFastPacketReassembler()
now = time.time()
payload = None
store = IdStore()

# Read all data from stdin
for TextString in sys.stdin:
	TextString = TextString.strip()
	if not TextString:
		continue  # skip empty lines

	try:
		if not ((TextString == "") or (TextString == "text")):
#			CanId, data_bytes = decodeBlueCtrlNativeCan(TextString)
			CanId, data_bytes = decodeYachtDevices(TextString)
			pgn_id = 0
			source_id, pgn_id, dest_id, priority = decodeCanId(CanId)
			

			if pgn_id in [
			126208,126464,126720,126983,126984,126985,126986,126987,126988,126996,126998,127233,127237,127489,127490,127491,
			127494,127495,127496,127497,127498,127503,127504,127506,127507,127509,127510,127511,127512,127513,127514,128275,
			128520,128538,129029,129038,129039,129040,129041,129044,129045,129284,129285,129301,129302,129538,129540,129541,
			129542,129545,129547,129549,129551,129556,129792,129793,129794,129795,129796,129797,129798,129799,129800,129801,
			129802,129803,129804,129805,129806,129807,129808,129809,129810,130052,130053,130054,130060,130061,130064,130065,
			130066,130067,130068,130069,130070,130071,130072,130073,130074,130320,130321,130322,130323,130324,130330,130561,
			130562,130563,130564,130565,130566,130567,130569,130570,130571,130572,130573,130574,130577,130578,130580,130581,
			130583,130584,130586,130816,130817,130818,130819,130820,130821,130822,130823,130824,130825,130827,130828,130831,
			130832,130833,130834,130835,130836,130837,130838,130839,130840,130842,130843,130845,130846,130847,130848,130850,
			130851,130856,130860,130880,130881,130918,130944
			]:
				payload = reasm.feed(pgn_id, source_id, dest_id, data_bytes)
				#print("---CanId: ",hex(CanId),"pgn_id:",pgn_id,"source_id:",source_id,"fast=True ","Frame & Sec",(data_bytes[0] >> 5) & 0x07, data_bytes[0] & 0x1F ,"payload:",list(data_bytes),flush=True)
				if payload is not None:
					pass
					#print("CanId: ",hex(CanId),"pgn_id:",pgn_id,"source_id:",source_id,"fast=True ","payload:",list(payload),flush=True)
			else:
				payload = data_bytes
				pass
#				#print("CanId: ",hex(CanId),"pgn_id:",pgn_id,"source_id:",source_id,"fast=False","payload:",list(payload),flush=True)

			if payload is not None:
				#print("CanId: ",hex(CanId),"pgn_id:",pgn_id,flush=True)
				#print("CanId: ",hex(CanId),"pgn_id:",pgn_id,"source_id:",source_id,"payload:",list(payload),flush=True)
				if pgn_id == 129025 and source_id == store.get(13868994483158255951) :
					print(pgn_id, source_id, list(payload), _s_le(payload, 0, 4)/10000000,_s_le(payload, 4, 4)/10000000, flush=True)
					pass
				if pgn_id == 129026 and source_id == store.get(13868994483158255951) :
					print(pgn_id, source_id, list(payload), _s_le(payload, 2, 2)*0.0001, _s_le(payload, 4, 2)*0.01, flush=True)
					pass
				if pgn_id == 127488 and payload[0]==0:
					pass
					#print(pgn_id, source_id, list(payload),_s_le(payload, 1, 2)*0.25, _s_le(payload, 3, 2)*0.1, flush=True)

				if pgn_id == 127488 and payload[0]==1:
					pass
					#print(pgn_id, source_id, list(payload),_s_le(payload, 1, 2)*0.25, _s_le(payload, 3, 2)*0.1, flush=True)

				if pgn_id == 127489 and payload[0]==0:
					pass
					#print(pgn_id, source_id, list(payload),_u_le(payload, 1, 2)*0.1,"kPa", _u_le(payload, 3, 2)*0.1-273,"°C", _u_le(payload, 5, 2)*0.01-273,"°C", _s_le(payload, 7, 2)*0.01,"V", _s_le(payload, 9, 2)*0.1,"l/h", _u_le(payload, 11, 4)*1/3600,"h",_u_le(payload, 15, 2)*0.1,"kPa",_u_le(payload, 17, 2)*1,"kPa", flush=True)

				if pgn_id == 127489 and payload[0]==1:
					pass
					#print(pgn_id, source_id, list(payload),_u_le(payload, 1, 2)*0.1,"kPa", _u_le(payload, 3, 2)*0.1-273,"°C", _u_le(payload, 5, 2)*0.01-273,"°C", _s_le(payload, 7, 2)*0.01,"V", _s_le(payload, 9, 2)*0.1,"l/h", _u_le(payload, 11, 4)*1/3600,"h",_u_le(payload, 15, 2)*0.1,"kPa",_u_le(payload, 17, 2)*1,"kPa", flush=True)

				if pgn_id == 60928:
					store.set(_u_le(payload, 0, 8), source_id)
					print(store.all(),flush=True)
					
					print(store.get(13868994483158255951),flush=True)



	except Exception as e:
		print(f"Error decoding line: {TextString!r}", flush=True)
		print(f"Split parts: {TextString.split()}", flush=True)
		print(f"{type(e).__name__}: {e}", flush=True)









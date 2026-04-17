import sys
import time

from n2k_decoder import (
	_s_le,
	_u_le,
	IdStore,
	N2kFastPacketReassembler,
	decodeCanId,
	decodeYachtDevices,
	decode_payload,
)

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
			

			payload = decode_payload(reasm, pgn_id, source_id, dest_id, data_bytes)

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







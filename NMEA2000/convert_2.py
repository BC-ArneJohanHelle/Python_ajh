import sys

from n2k_decoder import (
	_s_le,
	_u_le,
	decodeYachtDevices,
	store,
)

# Read all data from stdin
for TextString in sys.stdin:
	TextString = TextString.strip()
	if not TextString:
		continue  # skip empty lines

	try:
		if not ((TextString == "") or (TextString == "text")):
#			frame = decodeBlueCtrlNativeCan(TextString)
			frame = decodeYachtDevices(TextString)

			if frame.payload is not None:
				#print("CanId: ",hex(frame.can_id),"pgn_id:",frame.pgn_id,flush=True)
				#print("CanId: ",hex(frame.can_id),"pgn_id:",frame.pgn_id,"source_id:",frame.source_id,"payload:",list(frame.payload),flush=True)
				if frame.pgn_id == 129025 and frame.source_id == store.get(13868994483158255951) :
					print(frame.pgn_id, frame.source_id, list(frame.payload), _s_le(frame.payload, 0, 4)/10000000,_s_le(frame.payload, 4, 4)/10000000, flush=True)
					pass
				if frame.pgn_id == 129026 and frame.source_id == store.get(13868994483158255951) :
					print(frame.pgn_id, frame.source_id, list(frame.payload), _s_le(frame.payload, 2, 2)*0.0001, _s_le(frame.payload, 4, 2)*0.01, flush=True)
					pass
				if frame.pgn_id == 127488 and frame.payload[0]==0:
					pass
					#print(frame.pgn_id, frame.source_id, list(frame.payload),_s_le(frame.payload, 1, 2)*0.25, _s_le(frame.payload, 3, 2)*0.1, flush=True)

				if frame.pgn_id == 127488 and frame.payload[0]==1:
					pass
					#print(frame.pgn_id, frame.source_id, list(frame.payload),_s_le(frame.payload, 1, 2)*0.25, _s_le(frame.payload, 3, 2)*0.1, flush=True)

				if frame.pgn_id == 127489 and frame.payload[0]==0:
					pass
					#print(frame.pgn_id, frame.source_id, list(frame.payload),_u_le(frame.payload, 1, 2)*0.1,"kPa", _u_le(frame.payload, 3, 2)*0.1-273,"°C", _u_le(frame.payload, 5, 2)*0.01-273,"°C", _s_le(frame.payload, 7, 2)*0.01,"V", _s_le(frame.payload, 9, 2)*0.1,"l/h", _u_le(frame.payload, 11, 4)*1/3600,"h",_u_le(frame.payload, 15, 2)*0.1,"kPa",_u_le(frame.payload, 17, 2)*1,"kPa", flush=True)

				if frame.pgn_id == 127489 and frame.payload[0]==1:
					pass
					#print(frame.pgn_id, frame.source_id, list(frame.payload),_u_le(frame.payload, 1, 2)*0.1,"kPa", _u_le(frame.payload, 3, 2)*0.1-273,"°C", _u_le(frame.payload, 5, 2)*0.01-273,"°C", _s_le(frame.payload, 7, 2)*0.01,"V", _s_le(frame.payload, 9, 2)*0.1,"l/h", _u_le(frame.payload, 11, 4)*1/3600,"h",_u_le(frame.payload, 15, 2)*0.1,"kPa",_u_le(frame.payload, 17, 2)*1,"kPa", flush=True)

				if frame.pgn_id == 60928:
					print(store.all(),flush=True)
					
					print(store.get(13868994483158255951),flush=True)



	except Exception as e:
		print(f"Error decoding line: {TextString!r}", flush=True)
		print(f"Split parts: {TextString.split()}", flush=True)
		print(f"{type(e).__name__}: {e}", flush=True)



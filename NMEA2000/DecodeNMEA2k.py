import sys

from nmea2k import (
	read_signed_le_bits as _s,
	read_unsigned_le_bits as _u,
	decode_bluectrl_native_can,
)


def _print_header(f, title: str):
	print(f"\n{title}")
	print(f"source_id           : {f.source_id}")
	print(f"iso_name            : {f.iso_name}")


def _print_fields(*items):
	for label, value in items[:-1]:
		print(f"{label:<20}: {value}")
	if items:
		last_label, last_value = items[-1]
		print(f"{last_label:<20}: {last_value}", flush=True)


for TextString in sys.stdin:
	TextString = TextString.strip()
	if not TextString:
		continue

	try:
		if not ((TextString == "") or (TextString == "text")):
			f = decode_bluectrl_native_can(TextString)
			if f.payload is not None:
				pl = f.payload

				if f.pgn_id == 126992:
					sid = _u(pl, 0, 8)
					source = _u(pl, 8, 4)
					date_days = _u(pl, 16, 16)
					seconds_since_midnight = _u(pl, 32, 32) * 0.0001

					_print_header(f, "PGN 126992 (System Time) ------------")
					_print_fields(
						("sid", sid),
						("source", source),
						("date_days", date_days),
						("time", f"{seconds_since_midnight:.4f} s"),
					)

				if f.pgn_id == 127245:
					instance = _u(pl, 0, 8)
					direction_order = _u(pl, 8, 3)
					angle_order = _s(pl, 16, 16) * 0.0001
					position = _s(pl, 32, 16) * 0.0001

					_print_header(f, "PGN 127245 (Rudder) -----------------")
					_print_fields(
						("instance", instance),
						("direction_order", direction_order),
						("angle_order", f"{angle_order:.4f} rad"),
						("position", f"{position:.4f} rad"),
					)

				if f.pgn_id == 127250:
					sid = _u(pl, 0, 8)
					heading = _u(pl, 8, 16) * 0.0001
					deviation = _s(pl, 24, 16) * 0.0001
					variation = _s(pl, 40, 16) * 0.0001
					reference = _u(pl, 56, 2)

					_print_header(f, "PGN 127250 (Vessel Heading) ---------")
					_print_fields(
						("sid", sid),
						("heading", f"{heading:.4f} rad"),
						("deviation", f"{deviation:.4f} rad"),
						("variation", f"{variation:.4f} rad"),
						("reference", reference),
					)

				if f.pgn_id == 127257:
					sid = _u(pl, 0, 8)
					yaw = _s(pl, 8, 16) * 0.0001
					pitch = _s(pl, 24, 16) * 0.0001
					roll = _s(pl, 40, 16) * 0.0001

					_print_header(f, "PGN 127257 (Attitude) ---------------")
					_print_fields(
						("sid", sid),
						("yaw", f"{yaw:.4f} rad"),
						("pitch", f"{pitch:.4f} rad"),
						("roll", f"{roll:.4f} rad"),
					)

				if f.pgn_id == 127488:
					instance = _u(pl, 0, 8)
					speed = _u(pl, 8, 16) * 0.25
					boost_pressure = _u(pl, 24, 16) * 100
					tilt_trim = _s(pl, 40, 8)

					_print_header(f, "PGN 127488 (Engine Rapid Update) ----")
					_print_fields(
						("instance", instance),
						("speed", f"{speed:.2f} rpm"),
						("boost_pressure", f"{boost_pressure:.0f} Pa"),
						("tilt_trim", f"{tilt_trim} %"),
					)

				if f.pgn_id == 127489:
					instance = _u(pl, 0, 8)
					oil_pressure = _u(pl, 8, 16) * 100
					oil_temperature = _u(pl, 24, 16) * 0.1
					temperature = _u(pl, 40, 16) * 0.01
					alternator_potential = _s(pl, 56, 16) * 0.01
					fuel_rate = _s(pl, 72, 16) * 0.1
					total_engine_hours = _u(pl, 88, 32)
					coolant_pressure = _u(pl, 120, 16) * 100
					fuel_pressure = _u(pl, 136, 16) * 1000
					engine_load = _s(pl, 192, 8)
					engine_torque = _s(pl, 200, 8)

					_print_header(f, "PGN 127489 (Engine Dynamic) ---------")
					_print_fields(
						("instance", instance),
						("oil_pressure", f"{oil_pressure:.0f} Pa"),
						("oil_temperature", f"{oil_temperature:.1f} K"),
						("temperature", f"{temperature:.2f} K"),
						("alternator", f"{alternator_potential:.2f} V"),
						("fuel_rate", f"{fuel_rate:.1f} L/h"),
						("engine_hours", f"{total_engine_hours} s"),
						("coolant_pressure", f"{coolant_pressure:.0f} Pa"),
						("fuel_pressure", f"{fuel_pressure:.0f} Pa"),
						("engine_load", f"{engine_load} %"),
						("engine_torque", f"{engine_torque} %"),
					)

				if f.pgn_id == 127501:
					instance = _u(pl, 0, 8)
					indicator1 = _u(pl, 8, 2)
					indicator2 = _u(pl, 10, 2)
					indicator3 = _u(pl, 12, 2)
					indicator4 = _u(pl, 14, 2)

					_print_header(f, "PGN 127501 (Binary Switch Bank) -----")
					_print_fields(
						("instance", instance),
						("indicator1", indicator1),
						("indicator2", indicator2),
						("indicator3", indicator3),
						("indicator4", indicator4),
					)

				if f.pgn_id == 127505:
					instance = _u(pl, 0, 8)
					level = _u(pl, 8, 16) * 0.004
					type_ = _u(pl, 24, 8)

					_print_header(f, "PGN 127505 (Fluid Level) ------------")
					_print_fields(
						("instance", instance),
						("type", type_),
						("level", f"{level:.3f}"),
					)

				if f.pgn_id == 127507:
					instance = _u(pl, 0, 8)
					charger_state = _u(pl, 8, 8)
					voltage = _u(pl, 16, 16) * 0.01
					current = _s(pl, 32, 16) * 0.1

					_print_header(f, "PGN 127507 (Charger Status) ---------")
					_print_fields(
						("instance", instance),
						("charger_state", charger_state),
						("voltage", f"{voltage:.2f} V"),
						("current", f"{current:.1f} A"),
					)

				if f.pgn_id == 127508:
					instance = _u(pl, 0, 8)
					voltage = _s(pl, 8, 16) * 0.01
					current = _s(pl, 24, 16) * 0.1
					temperature = _u(pl, 40, 16) * 0.01

					_print_header(f, "PGN 127508 (Battery Status) ---------")
					_print_fields(
						("instance", instance),
						("voltage", f"{voltage:.2f} V"),
						("current", f"{current:.1f} A"),
						("temperature", f"{temperature:.2f} K"),
					)

				if f.pgn_id == 127509:
					instance = _u(pl, 0, 8)
					battery_voltage = _u(pl, 8, 16) * 0.01
					battery_current = _s(pl, 24, 16) * 0.1
					battery_temp = _u(pl, 40, 16) * 0.01

					_print_header(f, "PGN 127509 (Battery Status Extended) ")
					_print_fields(
						("instance", instance),
						("voltage", f"{battery_voltage:.2f} V"),
						("current", f"{battery_current:.1f} A"),
						("temperature", f"{battery_temp:.2f} K"),
					)

				if f.pgn_id == 128259:
					speed = _u(pl, 0, 16) * 0.01

					_print_header(f, "PGN 128259 (Speed) ------------------")
					_print_fields(("speed", f"{speed:.2f} m/s"))

				if f.pgn_id == 128267:
					depth = _u(pl, 8, 32) * 0.01

					_print_header(f, "PGN 128267 (Depth) ------------------")
					_print_fields(("depth", f"{depth:.2f} m"))

				if f.pgn_id == 128275:
					log = _u(pl, 0, 32)

					_print_header(f, "PGN 128275 (Distance Log) -----------")
					_print_fields(("log", log))

				if f.pgn_id == 129025:
					latitude = _s(pl, 0, 32) * 1e-7
					longitude = _s(pl, 32, 32) * 1e-7

					_print_header(f, "PGN 129025 (Position Rapid Update) --")
					_print_fields(
						("latitude", f"{latitude:.7f} deg"),
						("longitude", f"{longitude:.7f} deg"),
					)

				if f.pgn_id == 129026:
					sid = _u(pl, 0, 8)
					cog_reference = _u(pl, 8, 2)
					cog = _u(pl, 16, 16) * 0.0001
					sog = _u(pl, 32, 16) * 0.01

					_print_header(f, "PGN 129026 (COG & SOG) -------------")
					_print_fields(
						("sid", sid),
						("cog_reference", cog_reference),
						("cog", f"{cog:.4f} rad"),
						("sog", f"{sog:.2f} m/s"),
					)

				if f.pgn_id == 129033:
					date_days = _u(pl, 0, 16)
					seconds_since_midnight = _u(pl, 16, 32) * 0.0001
					local_offset = _s(pl, 48, 16) * 60

					_print_header(f, "PGN 129033 (Time & Date) -----------")
					_print_fields(
						("date_days", date_days),
						("time", f"{seconds_since_midnight:.4f} s"),
						("local_offset", f"{local_offset:.0f} s"),
					)

				if f.pgn_id == 129038:
					mmsi = _u(pl, 8, 32)
					sog = _u(pl, 42, 10) * 0.1
					cog = _u(pl, 52, 12) * 0.0001

					_print_header(f, "PGN 129038 (AIS Class A Position) ---")
					_print_fields(
						("mmsi", mmsi),
						("sog", f"{sog:.1f} kn"),
						("cog", f"{cog:.4f} rad"),
					)

				if f.pgn_id == 129039:
					mmsi = _u(pl, 8, 32)
					sog = _u(pl, 46, 10) * 0.1

					_print_header(f, "PGN 129039 (AIS Class B Position) ---")
					_print_fields(
						("mmsi", mmsi),
						("sog", f"{sog:.1f} kn"),
					)

				if f.pgn_id == 130306:
					wind_speed = _u(pl, 8, 16) * 0.01
					wind_angle = _u(pl, 24, 16) * 0.0001

					_print_header(f, "PGN 130306 (Wind) -------------------")
					_print_fields(
						("wind_speed", f"{wind_speed:.2f} m/s"),
						("wind_angle", f"{wind_angle:.4f} rad"),
					)

				if f.pgn_id == 130310:
					temp = _u(pl, 8, 16) * 0.01

					_print_header(f, "PGN 130310 (Temperature) ------------")
					_print_fields(("temperature", f"{temp:.2f} K"))

				if f.pgn_id == 130311:
					sid = _u(pl, 0, 8)
					temperature_source = _u(pl, 8, 6)
					humidity_source = _u(pl, 14, 2)
					temperature = _u(pl, 16, 16) * 0.01
					humidity = _s(pl, 32, 16) * 0.004
					atmospheric_pressure = _u(pl, 48, 16) * 100

					_print_header(f, "PGN 130311 (Environmental) ---------")
					_print_fields(
						("sid", sid),
						("temperature_source", temperature_source),
						("humidity_source", humidity_source),
						("temperature", f"{temperature:.2f} K"),
						("humidity", f"{humidity:.3f} %"),
						("pressure", f"{atmospheric_pressure:.0f} Pa"),
					)

				if f.pgn_id == 130312:
					temp = _u(pl, 8, 16) * 0.01

					_print_header(f, "PGN 130312 (Temperature) ------------")
					_print_fields(("temperature", f"{temp:.2f} K"))

				if f.pgn_id == 130314:
					sid = _u(pl, 0, 8)
					instance = _u(pl, 8, 8)
					source = _u(pl, 16, 8)
					pressure = _s(pl, 24, 32) * 0.1

					_print_header(f, "PGN 130314 (Actual Pressure) -------")
					_print_fields(
						("sid", sid),
						("instance", instance),
						("source", source),
						("pressure", f"{pressure:.1f} Pa"),
					)

				if f.pgn_id == 130316:
					sid = _u(pl, 0, 8)
					instance = _u(pl, 8, 8)
					source = _u(pl, 16, 8)
					temperature = _u(pl, 24, 24) * 0.001
					set_temperature = _u(pl, 48, 16) * 0.1

					_print_header(f, "PGN 130316 (Temp Extended Range) ---")
					_print_fields(
						("sid", sid),
						("instance", instance),
						("source", source),
						("temperature", f"{temperature:.3f} K"),
						("set_temperature", f"{set_temperature:.1f} K"),
					)

				if f.pgn_id == 130934:
					alert_id = _u(pl, 0, 16)
					alert_state = _u(pl, 16, 8)

					_print_header(f, "PGN 130934 (Alert) ------------------")
					_print_fields(
						("alert_id", alert_id),
						("alert_state", alert_state),
					)

				if f.pgn_id == 130935:
					alert_id = _u(pl, 0, 16)
					command = _u(pl, 16, 8)

					_print_header(f, "PGN 130935 (Alert Response) ---------")
					_print_fields(
						("alert_id", alert_id),
						("command", command),
					)

	except Exception as e:
		print(f"Error decoding line: {TextString!r}", flush=True)
		print(f"Split parts: {TextString.split()}", flush=True)
		print(f"{type(e).__name__}: {e}", flush=True)


import sys

from x_nmea2k_v1 import (
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
					sid = pl.to_uint(0, 8)
					source = pl.to_uint(8, 4)
					date_days = pl.to_uint(16, 16)
					seconds_since_midnight = pl.to_uint(32, 32) * 0.0001

					_print_header(f, "PGN 126992 (System Time) ------------")
					_print_fields(
						("sid", sid),
						("source", source),
						("date_days", date_days),
						("time", f"{seconds_since_midnight:.4f} s"),
					)

				if f.pgn_id == 127245:
					instance = pl.to_uint(0, 8)
					direction_order = pl.to_uint(8, 3)
					angle_order = pl.to_int(16, 16) * 0.0001
					position = pl.to_int(32, 16) * 0.0001

					_print_header(f, "PGN 127245 (Rudder) -----------------")
					_print_fields(
						("instance", instance),
						("direction_order", direction_order),
						("angle_order", f"{angle_order:.4f} rad"),
						("position", f"{position:.4f} rad"),
					)

				if f.pgn_id == 127250:
					sid = pl.to_uint(0, 8)
					heading = pl.to_uint(8, 16) * 0.0001
					deviation = pl.to_int(24, 16) * 0.0001
					variation = pl.to_int(40, 16) * 0.0001
					reference = pl.to_uint(56, 2)

					_print_header(f, "PGN 127250 (Vessel Heading) ---------")
					_print_fields(
						("sid", sid),
						("heading", f"{heading:.4f} rad"),
						("deviation", f"{deviation:.4f} rad"),
						("variation", f"{variation:.4f} rad"),
						("reference", reference),
					)

				if f.pgn_id == 127257:
					sid = pl.to_uint(0, 8)
					yaw = pl.to_int(8, 16) * 0.0001
					pitch = pl.to_int(24, 16) * 0.0001
					roll = pl.to_int(40, 16) * 0.0001

					_print_header(f, "PGN 127257 (Attitude) ---------------")
					_print_fields(
						("sid", sid),
						("yaw", f"{yaw:.4f} rad"),
						("pitch", f"{pitch:.4f} rad"),
						("roll", f"{roll:.4f} rad"),
					)

				if f.pgn_id == 127488:
					instance = pl.to_uint(0, 8)
					speed = pl.to_uint(8, 16) * 0.25
					boost_pressure = pl.to_uint(24, 16) * 100
					tilt_trim = pl.to_int(40, 8)

					_print_header(f, "PGN 127488 (Engine Rapid Update) ----")
					_print_fields(
						("instance", instance),
						("speed", f"{speed:.2f} rpm"),
						("boost_pressure", f"{boost_pressure:.0f} Pa"),
						("tilt_trim", f"{tilt_trim} %"),
					)

				if f.pgn_id == 127489:
					instance = pl.to_uint(0, 8)
					oil_pressure = pl.to_uint(8, 16) * 100
					oil_temperature = pl.to_uint(24, 16) * 0.1
					temperature = pl.to_uint(40, 16) * 0.01
					alternator_potential = pl.to_int(56, 16) * 0.01
					fuel_rate = pl.to_int(72, 16) * 0.1
					total_engine_hours = pl.to_uint(88, 32)
					coolant_pressure = pl.to_uint(120, 16) * 100
					fuel_pressure = pl.to_uint(136, 16) * 1000
					engine_load = pl.to_int(192, 8)
					engine_torque = pl.to_int(200, 8)

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
					instance = pl.to_uint(0, 8)
					indicator1 = pl.to_uint(8, 2)
					indicator2 = pl.to_uint(10, 2)
					indicator3 = pl.to_uint(12, 2)
					indicator4 = pl.to_uint(14, 2)

					_print_header(f, "PGN 127501 (Binary Switch Bank) -----")
					_print_fields(
						("instance", instance),
						("indicator1", indicator1),
						("indicator2", indicator2),
						("indicator3", indicator3),
						("indicator4", indicator4),
					)

				if f.pgn_id == 127505:
					instance = pl.to_uint(0, 8)
					level = pl.to_uint(8, 16) * 0.004
					type_ = pl.to_uint(24, 8)

					_print_header(f, "PGN 127505 (Fluid Level) ------------")
					_print_fields(
						("instance", instance),
						("type", type_),
						("level", f"{level:.3f}"),
					)

				if f.pgn_id == 127507:
					instance = pl.to_uint(0, 8)
					charger_state = pl.to_uint(8, 8)
					voltage = pl.to_uint(16, 16) * 0.01
					current = pl.to_int(32, 16) * 0.1

					_print_header(f, "PGN 127507 (Charger Status) ---------")
					_print_fields(
						("instance", instance),
						("charger_state", charger_state),
						("voltage", f"{voltage:.2f} V"),
						("current", f"{current:.1f} A"),
					)

				if f.pgn_id == 127508:
					instance = pl.to_uint(0, 8)
					voltage = pl.to_int(8, 16) * 0.01
					current = pl.to_int(24, 16) * 0.1
					temperature = pl.to_uint(40, 16) * 0.01

					_print_header(f, "PGN 127508 (Battery Status) ---------")
					_print_fields(
						("instance", instance),
						("voltage", f"{voltage:.2f} V"),
						("current", f"{current:.1f} A"),
						("temperature", f"{temperature:.2f} K"),
					)

				if f.pgn_id == 127509:
					instance = pl.to_uint(0, 8)
					battery_voltage = pl.to_uint(8, 16) * 0.01
					battery_current = pl.to_int(24, 16) * 0.1
					battery_temp = pl.to_uint(40, 16) * 0.01

					_print_header(f, "PGN 127509 (Battery Status Extended) ")
					_print_fields(
						("instance", instance),
						("voltage", f"{battery_voltage:.2f} V"),
						("current", f"{battery_current:.1f} A"),
						("temperature", f"{battery_temp:.2f} K"),
					)

				if f.pgn_id == 128259:
					speed = pl.to_uint(0, 16) * 0.01

					_print_header(f, "PGN 128259 (Speed) ------------------")
					_print_fields(("speed", f"{speed:.2f} m/s"))

				if f.pgn_id == 128267:
					depth = pl.to_uint(8, 32) * 0.01

					_print_header(f, "PGN 128267 (Depth) ------------------")
					_print_fields(("depth", f"{depth:.2f} m"))

				if f.pgn_id == 128275:
					log = pl.to_uint(0, 32)

					_print_header(f, "PGN 128275 (Distance Log) -----------")
					_print_fields(("log", log))

				if f.pgn_id == 129025:
					latitude = pl.to_int(0, 32) * 1e-7
					longitude = pl.to_int(32, 32) * 1e-7

					_print_header(f, "PGN 129025 (Position Rapid Update) --")
					_print_fields(
						("latitude", f"{latitude:.7f} deg"),
						("longitude", f"{longitude:.7f} deg"),
					)

				if f.pgn_id == 129026:
					sid = pl.to_uint(0, 8)
					cog_reference = pl.to_uint(8, 2)
					cog = pl.to_uint(16, 16) * 0.0001
					sog = pl.to_uint(32, 16) * 0.01

					_print_header(f, "PGN 129026 (COG & SOG) -------------")
					_print_fields(
						("sid", sid),
						("cog_reference", cog_reference),
						("cog", f"{cog:.4f} rad"),
						("sog", f"{sog:.2f} m/s"),
					)

				if f.pgn_id == 129033:
					date_days = pl.to_uint(0, 16)
					seconds_since_midnight = pl.to_uint(16, 32) * 0.0001
					local_offset = pl.to_int(48, 16) * 60

					_print_header(f, "PGN 129033 (Time & Date) -----------")
					_print_fields(
						("date_days", date_days),
						("time", f"{seconds_since_midnight:.4f} s"),
						("local_offset", f"{local_offset:.0f} s"),
					)

				if f.pgn_id == 129038:
					mmsi = pl.to_uint(8, 32)
					sog = pl.to_uint(42, 10) * 0.1
					cog = pl.to_uint(52, 12) * 0.0001

					_print_header(f, "PGN 129038 (AIS Class A Position) ---")
					_print_fields(
						("mmsi", mmsi),
						("sog", f"{sog:.1f} kn"),
						("cog", f"{cog:.4f} rad"),
					)

				if f.pgn_id == 129039:
					mmsi = pl.to_uint(8, 32)
					sog = pl.to_uint(46, 10) * 0.1

					_print_header(f, "PGN 129039 (AIS Class B Position) ---")
					_print_fields(
						("mmsi", mmsi),
						("sog", f"{sog:.1f} kn"),
					)

				if f.pgn_id == 130306:
					wind_speed = pl.to_uint(8, 16) * 0.01
					wind_angle = pl.to_uint(24, 16) * 0.0001

					_print_header(f, "PGN 130306 (Wind) -------------------")
					_print_fields(
						("wind_speed", f"{wind_speed:.2f} m/s"),
						("wind_angle", f"{wind_angle:.4f} rad"),
					)

				if f.pgn_id == 130310:
					temp = pl.to_uint(8, 16) * 0.01

					_print_header(f, "PGN 130310 (Temperature) ------------")
					_print_fields(("temperature", f"{temp:.2f} K"))

				if f.pgn_id == 130311:
					sid = pl.to_uint(0, 8)
					temperature_source = pl.to_uint(8, 6)
					humidity_source = pl.to_uint(14, 2)
					temperature = pl.to_uint(16, 16) * 0.01
					humidity = pl.to_int(32, 16) * 0.004
					atmospheric_pressure = pl.to_uint(48, 16) * 100

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
					temp = pl.to_uint(8, 16) * 0.01

					_print_header(f, "PGN 130312 (Temperature) ------------")
					_print_fields(("temperature", f"{temp:.2f} K"))

				if f.pgn_id == 130314:
					sid = pl.to_uint(0, 8)
					instance = pl.to_uint(8, 8)
					source = pl.to_uint(16, 8)
					pressure = pl.to_int(24, 32) * 0.1

					_print_header(f, "PGN 130314 (Actual Pressure) -------")
					_print_fields(
						("sid", sid),
						("instance", instance),
						("source", source),
						("pressure", f"{pressure:.1f} Pa"),
					)

				if f.pgn_id == 130316:
					sid = pl.to_uint(0, 8)
					instance = pl.to_uint(8, 8)
					source = pl.to_uint(16, 8)
					temperature = pl.to_uint(24, 24) * 0.001
					set_temperature = pl.to_uint(48, 16) * 0.1

					_print_header(f, "PGN 130316 (Temp Extended Range) ---")
					_print_fields(
						("sid", sid),
						("instance", instance),
						("source", source),
						("temperature", f"{temperature:.3f} K"),
						("set_temperature", f"{set_temperature:.1f} K"),
					)

				if f.pgn_id == 130934:
					alert_id = pl.to_uint(0, 16)
					alert_state = pl.to_uint(16, 8)

					_print_header(f, "PGN 130934 (Alert) ------------------")
					_print_fields(
						("alert_id", alert_id),
						("alert_state", alert_state),
					)

				if f.pgn_id == 130935:
					alert_id = pl.to_uint(0, 16)
					command = pl.to_uint(16, 8)

					_print_header(f, "PGN 130935 (Alert Response) ---------")
					_print_fields(
						("alert_id", alert_id),
						("command", command),
					)

	except Exception as e:
		print(f"Error decoding line: {TextString!r}", flush=True)
		print(f"Split parts: {TextString.split()}", flush=True)
		print(f"{type(e).__name__}: {e}", flush=True)

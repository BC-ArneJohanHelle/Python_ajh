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


def _scale(value, factor):
	return value * factor if value is not None else None


def _fmt(value, spec: str, unit: str = ""):
	if value is None:
		return None
	return f"{value:{spec}}{unit}"


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
					seconds_since_midnight = _scale(pl.to_uint(32, 32), 0.0001)

					_print_header(f, "PGN 126992 (System Time) ------------")
					_print_fields(
						("sid", sid),
						("source", source),
						("date_days", date_days),
						("time", _fmt(seconds_since_midnight, ".4f", " s")),
					)

				if f.pgn_id == 126996:
					nmea2000_version = _scale(pl.to_uint(0, 16), 0.001)
					product_code = pl.to_uint(16, 16)
					model_id = pl.to_string_fix(32, 256)
					software_version_code = pl.to_string_fix(288, 256)
					model_version = pl.to_string_fix(544, 256)
					model_serial_code = pl.to_string_fix(800, 256)
					certification_level = pl.to_uint(1056, 8)
					load_equivalency = pl.to_uint(1064, 8)

					_print_header(f, "PGN 126996 (Product Information) ---")
					_print_fields(
						(
							"nmea2000_version",
							_fmt(nmea2000_version, ".3f"),
						),
						("product_code", product_code),
						("model_id", model_id),
						("software_version", software_version_code),
						("model_version", model_version),
						("model_serial", model_serial_code),
						("certification_level", certification_level),
						("load_equivalency", load_equivalency),
					)

				if f.pgn_id == 127245:
					instance = pl.to_uint(0, 8)
					direction_order = pl.to_uint(8, 3)
					angle_order = _scale(pl.to_int(16, 16), 0.0001)
					position = _scale(pl.to_int(32, 16), 0.0001)

					_print_header(f, "PGN 127245 (Rudder) -----------------")
					_print_fields(
						("instance", instance),
						("direction_order", direction_order),
						("angle_order", _fmt(angle_order, ".4f", " rad")),
						("position", _fmt(position, ".4f", " rad")),
					)

				if f.pgn_id == 127250:
					sid = pl.to_uint(0, 8)
					heading = _scale(pl.to_uint(8, 16), 0.0001)
					deviation = _scale(pl.to_int(24, 16), 0.0001)
					variation = _scale(pl.to_int(40, 16), 0.0001)
					reference = pl.to_uint(56, 2)

					_print_header(f, "PGN 127250 (Vessel Heading) ---------")
					_print_fields(
						("sid", sid),
						("heading", _fmt(heading, ".4f", " rad")),
						("deviation", _fmt(deviation, ".4f", " rad")),
						("variation", _fmt(variation, ".4f", " rad")),
						("reference", reference),
					)

				if f.pgn_id == 127257:
					sid = pl.to_uint(0, 8)
					yaw = _scale(pl.to_int(8, 16), 0.0001)
					pitch = _scale(pl.to_int(24, 16), 0.0001)
					roll = _scale(pl.to_int(40, 16), 0.0001)

					_print_header(f, "PGN 127257 (Attitude) ---------------")
					_print_fields(
						("sid", sid),
						("yaw", _fmt(yaw, ".4f", " rad")),
						("pitch", _fmt(pitch, ".4f", " rad")),
						("roll", _fmt(roll, ".4f", " rad")),
					)

				if f.pgn_id == 127488:
					instance = pl.to_uint(0, 8)
					speed = _scale(pl.to_uint(8, 16), 0.25)
					boost_pressure = _scale(pl.to_uint(24, 16), 100)
					tilt_trim = pl.to_int(40, 8)

					_print_header(f, "PGN 127488 (Engine Rapid Update) ----")
					_print_fields(
						("instance", instance),
						("speed", _fmt(speed, ".2f", " rpm")),
						("boost_pressure", _fmt(boost_pressure, ".0f", " Pa")),
						("tilt_trim", f"{tilt_trim} %"),
					)

				if f.pgn_id == 127489:
					instance = pl.to_uint(0, 8)
					oil_pressure = _scale(pl.to_uint(8, 16), 100)
					oil_temperature = _scale(pl.to_uint(24, 16), 0.1)
					temperature = _scale(pl.to_uint(40, 16), 0.01)
					alternator_potential = _scale(pl.to_int(56, 16), 0.01)
					fuel_rate = _scale(pl.to_int(72, 16), 0.1)
					total_engine_hours = pl.to_uint(88, 32)
					coolant_pressure = _scale(pl.to_uint(120, 16), 100)
					fuel_pressure = _scale(pl.to_uint(136, 16), 1000)
					engine_load = pl.to_int(192, 8)
					engine_torque = pl.to_int(200, 8)

					_print_header(f, "PGN 127489 (Engine Dynamic) ---------")
					_print_fields(
						("instance", instance),
						("oil_pressure", _fmt(oil_pressure, ".0f", " Pa")),
						("oil_temperature", _fmt(oil_temperature, ".1f", " K")),
						("temperature", _fmt(temperature, ".2f", " K")),
						("alternator", _fmt(alternator_potential, ".2f", " V")),
						("fuel_rate", _fmt(fuel_rate, ".1f", " L/h")),
						("engine_hours", f"{total_engine_hours} s"),
						("coolant_pressure", _fmt(coolant_pressure, ".0f", " Pa")),
						("fuel_pressure", _fmt(fuel_pressure, ".0f", " Pa")),
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
					level = _scale(pl.to_uint(8, 16), 0.004)
					type_ = pl.to_uint(24, 8)

					_print_header(f, "PGN 127505 (Fluid Level) ------------")
					_print_fields(
						("instance", instance),
						("type", type_),
						("level", _fmt(level, ".3f")),
					)

				if f.pgn_id == 127506:
					sid = pl.to_uint(0, 8)
					instance = pl.to_uint(8, 8)
					dc_type = pl.to_uint(16, 8)
					state_of_charge = pl.to_uint(24, 8)
					state_of_health = pl.to_uint(32, 8)
					time_remaining = _scale(pl.to_uint(40, 16), 60)
					ripple_voltage = _scale(pl.to_uint(56, 16), 0.001)
					remaining_capacity = _scale(pl.to_uint(72, 16), 3600)

					_print_header(f, "PGN 127506 (DC Detailed Status) -----")
					_print_fields(
						("sid", sid),
						("instance", instance),
						("dc_type", dc_type),
						("state_of_charge", f"{state_of_charge} %"),
						("state_of_health", f"{state_of_health} %"),
						("time_remaining", f"{time_remaining} s"),
						("ripple_voltage", _fmt(ripple_voltage, ".3f", " V")),
						("remaining_capacity", f"{remaining_capacity} C"),
					)

				if f.pgn_id == 127507:
					instance = pl.to_uint(0, 8)
					charger_state = pl.to_uint(8, 8)
					voltage = _scale(pl.to_uint(16, 16), 0.01)
					current = _scale(pl.to_int(32, 16), 0.1)

					_print_header(f, "PGN 127507 (Charger Status) ---------")
					_print_fields(
						("instance", instance),
						("charger_state", charger_state),
						("voltage", _fmt(voltage, ".2f", " V")),
						("current", _fmt(current, ".1f", " A")),
					)

				if f.pgn_id == 127508:
					instance = pl.to_uint(0, 8)
					voltage = _scale(pl.to_int(8, 16), 0.01)
					current = _scale(pl.to_int(24, 16), 0.1)
					temperature = _scale(pl.to_uint(40, 16), 0.01)

					_print_header(f, "PGN 127508 (Battery Status) ---------")
					_print_fields(
						("instance", instance),
						("voltage", _fmt(voltage, ".2f", " V")),
						("current", _fmt(current, ".1f", " A")),
						("temperature", _fmt(temperature, ".2f", " K")),
					)

				if f.pgn_id == 127509:
					instance = pl.to_uint(0, 8)
					battery_voltage = _scale(pl.to_uint(8, 16), 0.01)
					battery_current = _scale(pl.to_int(24, 16), 0.1)
					battery_temp = _scale(pl.to_uint(40, 16), 0.01)

					_print_header(f, "PGN 127509 (Battery Status Extended) ")
					_print_fields(
						("instance", instance),
						("voltage", _fmt(battery_voltage, ".2f", " V")),
						("current", _fmt(battery_current, ".1f", " A")),
						("temperature", _fmt(battery_temp, ".2f", " K")),
					)

				if f.pgn_id == 128259:
					speed = _scale(pl.to_uint(0, 16), 0.01)

					_print_header(f, "PGN 128259 (Speed) ------------------")
					_print_fields(("speed", _fmt(speed, ".2f", " m/s")))

				if f.pgn_id == 128267:
					depth = _scale(pl.to_uint(8, 32), 0.01)

					_print_header(f, "PGN 128267 (Depth) ------------------")
					_print_fields(("depth", _fmt(depth, ".2f", " m")))

				if f.pgn_id == 128275:
					log = pl.to_uint(0, 32)

					_print_header(f, "PGN 128275 (Distance Log) -----------")
					_print_fields(("log", log))

				if f.pgn_id == 129025:
					latitude = _scale(pl.to_int(0, 32), 1e-7)
					longitude = _scale(pl.to_int(32, 32), 1e-7)

					_print_header(f, "PGN 129025 (Position Rapid Update) --")
					_print_fields(
						("latitude", _fmt(latitude, ".7f", " deg")),
						("longitude", _fmt(longitude, ".7f", " deg")),
					)

				if f.pgn_id == 129026:
					sid = pl.to_uint(0, 8)
					cog_reference = pl.to_uint(8, 2)
					cog = _scale(pl.to_uint(16, 16), 0.0001)
					sog = _scale(pl.to_uint(32, 16), 0.01)

					_print_header(f, "PGN 129026 (COG & SOG) -------------")
					_print_fields(
						("sid", sid),
						("cog_reference", cog_reference),
						("cog", _fmt(cog, ".4f", " rad")),
						("sog", _fmt(sog, ".2f", " m/s")),
					)

				if f.pgn_id == 129033:
					date_days = pl.to_uint(0, 16)
					seconds_since_midnight = _scale(pl.to_uint(16, 32), 0.0001)
					local_offset = _scale(pl.to_int(48, 16), 60)

					_print_header(f, "PGN 129033 (Time & Date) -----------")
					_print_fields(
						("date_days", date_days),
						("time", _fmt(seconds_since_midnight, ".4f", " s")),
						("local_offset", _fmt(local_offset, ".0f", " s")),
					)

				if f.pgn_id == 129038:
					mmsi = pl.to_uint(8, 32)
					sog = _scale(pl.to_uint(42, 10), 0.1)
					cog = _scale(pl.to_uint(52, 12), 0.0001)

					_print_header(f, "PGN 129038 (AIS Class A Position) ---")
					_print_fields(
						("mmsi", mmsi),
						("sog", _fmt(sog, ".1f", " kn")),
						("cog", _fmt(cog, ".4f", " rad")),
					)

				if f.pgn_id == 129039:
					mmsi = pl.to_uint(8, 32)
					sog = _scale(pl.to_uint(46, 10), 0.1)

					_print_header(f, "PGN 129039 (AIS Class B Position) ---")
					_print_fields(
						("mmsi", mmsi),
						("sog", _fmt(sog, ".1f", " kn")),
					)

				if f.pgn_id == 130306:
					wind_speed = _scale(pl.to_uint(8, 16), 0.01)
					wind_angle = _scale(pl.to_uint(24, 16), 0.0001)

					_print_header(f, "PGN 130306 (Wind) -------------------")
					_print_fields(
						("wind_speed", _fmt(wind_speed, ".2f", " m/s")),
						("wind_angle", _fmt(wind_angle, ".4f", " rad")),
					)

				if f.pgn_id == 130310:
					temp = _scale(pl.to_uint(8, 16), 0.01)

					_print_header(f, "PGN 130310 (Temperature) ------------")
					_print_fields(("temperature", _fmt(temp, ".2f", " K")))

				if f.pgn_id == 130311:
					sid = pl.to_uint(0, 8)
					temperature_source = pl.to_uint(8, 6)
					humidity_source = pl.to_uint(14, 2)
					temperature = _scale(pl.to_uint(16, 16), 0.01)
					humidity = _scale(pl.to_int(32, 16), 0.004)
					atmospheric_pressure = _scale(pl.to_uint(48, 16), 100)

					_print_header(f, "PGN 130311 (Environmental) ---------")
					_print_fields(
						("sid", sid),
						("temperature_source", temperature_source),
						("humidity_source", humidity_source),
						("temperature", _fmt(temperature, ".2f", " K")),
						("humidity", _fmt(humidity, ".3f", " %")),
						("pressure", _fmt(atmospheric_pressure, ".0f", " Pa")),
					)

				if f.pgn_id == 130312:
					temp = _scale(pl.to_uint(8, 16), 0.01)

					_print_header(f, "PGN 130312 (Temperature) ------------")
					_print_fields(("temperature", _fmt(temp, ".2f", " K")))

				if f.pgn_id == 130314:
					sid = pl.to_uint(0, 8)
					instance = pl.to_uint(8, 8)
					source = pl.to_uint(16, 8)
					pressure = _scale(pl.to_int(24, 32), 0.1)

					_print_header(f, "PGN 130314 (Actual Pressure) -------")
					_print_fields(
						("sid", sid),
						("instance", instance),
						("source", source),
						("pressure", _fmt(pressure, ".1f", " Pa")),
					)

				if f.pgn_id == 130316:
					sid = pl.to_uint(0, 8)
					instance = pl.to_uint(8, 8)
					source = pl.to_uint(16, 8)
					temperature = _scale(pl.to_uint(24, 24), 0.001)
					set_temperature = _scale(pl.to_uint(48, 16), 0.1)

					_print_header(f, "PGN 130316 (Temp Extended Range) ---")
					_print_fields(
						("sid", sid),
						("instance", instance),
						("source", source),
						("temperature", _fmt(temperature, ".3f", " K")),
						("set_temperature", _fmt(set_temperature, ".1f", " K")),
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

				if f.pgn_id == 60928:
					unique_number = pl.to_uint(0, 21)
					manufacturer_code = pl.to_uint(21, 11)
					device_instance_lower = pl.to_uint(32, 3)
					device_instance_upper = pl.to_uint(35, 5)
					device_function = pl.to_uint(40, 8)
					spare = pl.to_uint(48, 1)
					device_class = pl.to_uint(49, 7)
					system_instance = pl.to_uint(56, 4)
					industry_group = pl.to_uint(60, 3)
					arbitrary_address_capable = pl.to_uint(63, 1)

					_print_header(f, "PGN 60928 (ISO Address Claim) ------")
					_print_fields(
						("unique_number", unique_number),
						("manufacturer_code", manufacturer_code),
						("device_instance_lower", device_instance_lower),
						("device_instance_upper", device_instance_upper),
						("device_function", device_function),
						("spare", spare),
						("device_class", device_class),
						("system_instance", system_instance),
						("industry_group", industry_group),
						("arbitrary_address", arbitrary_address_capable),
					)

	except Exception as e:
		print(f"Error decoding line: {TextString!r}", flush=True)
		print(f"Split parts: {TextString.split()}", flush=True)
		print(f"{type(e).__name__}: {e}", flush=True)

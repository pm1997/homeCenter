import RPi.GPIO as GPIO
from constants import VALID_PINS

class Util:

	def check_string(str1):
		# cut string at length 40
		try:
			return ((str(str1))[:40] + '..') if len(str1) > 40 else str(str1)
		except:
			return "ERROR"

	def turn_led_on(nr):
		if GPIO.input(nr) == 0:
			GPIO.output(nr, 1)

	def turn_led_off(nr):
		if GPIO.input(nr) == 1:
			GPIO.output(nr, 0)

	def check_config(new_config):
		# checl if valid config provided
		try:
			_, no_error = Util.harden_config_input(new_config)
			return no_error
		except:
			return False

	def harden_config_input(new_config):
		# store new config secure
		n_rooms = new_config["rooms"]
		n_all_off = bool(new_config["all_disabled"])
		r_config=[]
		no_error = True
		print(new_config)
		for r in n_rooms:
			name = str(r["room_name"])
			pin = int(r["room_gpio"])
			d_on = bool(r["default_on"])
			a_on = bool (r["alarm_on"])
			if (pin not in VALID_PINS):
				no_error = False

			r_config.append({
					"room_name": name,
					"room_gpio": pin,
					"default_on": d_on,
					"alarm_on": a_on
			})
		conf = {
			"rooms": r_config,
			"all_disabled": n_all_off
		}
		return conf, no_error

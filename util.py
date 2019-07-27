import RPi.GPIO as GPIO

class Util:

	def check_string(str1):
		try:
			return str(str1)
		except:
			return "ERROR"

	def turn_led_on(nr):
		if GPIO.input(nr) == 0:
			GPIO.output(nr, 1)

	def turn_led_off(nr):
		if GPIO.input(nr) == 1:
			GPIO.output(nr, 0)

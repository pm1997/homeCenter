import RPi.GPIO as GPIO
from constants import VALID_PINS, INVALID_PIN, OFF

class Room:

	def __init__(self, pin, name, default_on=True, activated=True ):
		if pin in VALID_PINS:
			self._pin = pin
			self._name = name
			self._default_on = default_on
			self._activated = activated
			GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
		else:
			self._name = "ERROR"
			self._activated = self._default_on = False
			self._pin = INVALID_PIN

	def state(self):
		if self._pin == INVALID_PIN :
			return OFF
		self._state = GPIO.input(self._pin)
		return self._state

	def pin(self):
		return self._pin

	def change_pin(self, new_pin):
		if pin in VALID_PINS:
			self._pin = new_pin
			GPIO.setup( new_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
		else:
			self._name = "ERROR"
			self._activated = self._default_on = False
			self._pin = INVALID_PIN

	def activate(self):
		return self._activated

	def change_mode(self, newMode):
		self._activated = newMode == True

	def reset(self):
		self._activated = self._default_on

	def default(self):
		return self._default_on

	def change_default(self, newDefault):
		self._default = newDefault == True

	def name(self):
		return self._name

	def change_name(self, new_name):
		self._name = new_name

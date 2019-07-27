import RPi.GPIO as GPIO
from constants import VALID_PINS, INVALID_PIN, OFF
from util import Util

class Room:

	def __init__(self, pin, name, default_on=True, activated=True ):
		# init only correctly if valid pin is given
		if pin in VALID_PINS:
			self._pin = pin
			self._name = Util.check_string(name)
			self._default_on = default_on == True
			self._activated = activated == True
			GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
		else:
			self._name = "ERROR"
			self._activated = self._default_on = False
			self._pin = INVALID_PIN

	def state(self):
		# get current room state
		if self._pin == INVALID_PIN :
			return OFF
		self._state = GPIO.input(self._pin)
		return self._state

	def pin(self):
		return self._pin

	def change_pin(self, new_pin):
		# change used gpio pin
		# for later use
		if pin in VALID_PINS:
			self._pin = new_pin
			GPIO.setup( new_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
		else:
			self._name = "ERROR"
			self._activated = self._default_on = False
			self._pin = INVALID_PIN

	def activated(self):
		return self._activated

	def change_mode(self, newMode):
		# secured set new mode
		self._activated = bool(newMode)

	def reset(self):
		self._activated = self._default_on

	def default(self):
		return self._default_on

	def change_default(self, newDefault):
		self._default = bool(newDefault)

	def name(self):
		return self._name

	def change_name(self, new_name):
		#set new name if given valid name
		self._name = Util.check_string(new_name)

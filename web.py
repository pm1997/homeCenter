#!/usr/bin/python

from flask import request
from flask_api import FlaskAPI
import RPi.GPIO as GPIO
from util import Util
from datetime import datetime

import threading

from room import Room

LEDS = {}
def init_leds():
	global LEDS
	LEDS = {"green": 3, "orange": 5, "red": 7}
	GPIO.setmode(GPIO.BOARD)
	for led in LEDS:
		print(led)
		GPIO.setup(LEDS[led], GPIO.OUT)

init_leds()

# add initial rooms 
# rooms can be added or remove via api
r1 = Room(29, "Küche")
r2 = Room(31, "Billiardzimmer")
r3 = Room(33, "Klavierzimmer")
r4 = Room(35, "Eisenbahnzimmer")
r5 = Room(37, "Wirtschaftsraum")

# init global variables
rooms = [ r1, r2, r3, r4, r5 ]
config = {"all_disabled": False}
app = FlaskAPI(__name__)

@app.route('/', methods=["GET"])
def api_root():
	# root web api page
	# print information
	return {
		"config:": request.url + "config",
		"alarm:": request.url + "alarm",
		"led_url": request.url + "led/( green | orange | red )/"
	}


@app.route('/config/', methods=["GET"])
def get_config():
	# change gloabl variable 'config'
	# at first run, init config
	global config
	r_configs = list()
	global rooms
	for r in rooms:
		# create config object foreach room
		room_config = { "room_name": r.name(),
				"room_gpio": r.pin(),
				"default_on": r.default(), # reserved for later use of api
				"alarm_on": r.activated()
				}
		r_configs.append(room_config)
	
	config = {
		 "rooms" : r_configs,
		"all_disabled": bool(config["all_disabled"]) # turn off all rooms
		}
	return config

@app.route('/setconfig/', methods=["GET","POST"])
def set_config():
	global config
	# print config at GET and POST; change it only on POST
	#check for valid config
	if request.method == "POST" and Util.check_config(request.data):
		# use only neccessary parts of request.data and prevent injection
		config, _ = Util.harden_config_input(request.data)
		print(f"{datetime.now()}: update config")
		print(config)
		# rebuild global var 'rooms'
		global rooms
		rooms=[]
		for r in config["rooms"]:
			# will init GPIO pins
			rooms.append(Room(pin=r["room_gpio"], name=r["room_name"], default_on=r["default_on"], activated=r["alarm_on"]))
	return config

@app.route('/alarm/', methods=["GET"])
def api_alarm_control():
	# get state of red LED (alarm)
	check_alarm_state()
	return {"alarm_state": GPIO.input(LEDS["red"])}


@app.route('/led/<color>/', methods=["GET"])
def api_led_control(color):
	return {color: GPIO.input(LEDS[color])}


# main function to calculate alarm
def check_alarm_state():
	get_config()
	global config
	# if alarm global disabled turn on orange LED
	if bool(config["all_disabled"]):
		Util.turn_led_on(LEDS["orange"])
	else:
		Util.turn_led_off(LEDS["orange"])
	all_ok = True # all rooms  closed and no alarm
	all_closed = True # all rooms closed
	# check room state for each room
	for r in config["rooms"]:
		# because of usage of relays:
		# INPUT: 0 => room open
		# INPUT: 1 => room closed
		if not GPIO.input(r["room_gpio"]):
			all_closed = False
			Util.turn_led_off(LEDS["green"])
			if r["alarm_on"] and not config["all_disabled"]:
				# print alarm and turn red LED on
				print(f"{datetime.now()}: Alarm enabled and room {r['room_name']} open!")
				Util.turn_led_on(LEDS["red"])
				all_ok = False
	# if all closed the green LED is on
	# if one room is open the green LED is off and 
	#	depending of the config the red LED on 
	if all_ok:
		if all_closed:
			Util.turn_led_on(LEDS["green"])
		Util.turn_led_off(LEDS["red"])

def timer():
	# check current room state every 0.4 seconds
	check_alarm_state()
	threading.Timer(0.4, timer).start()


if __name__ == "__main__":
	app.run()

timer()

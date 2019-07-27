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

r1 = Room(29, "Küche")
r2 = Room(31, "Billiardzimmer")
r3 = Room(33, "Klavierzimmer")
r4 = Room(35, "Eisenbahnzimmer")
r5 = Room(37, "Wirtschaftsraum")

rooms = [ r1, r2, r3, r4, r5 ]
config = {"all_disabled": False}
app = FlaskAPI(__name__)

@app.route('/', methods=["GET"])
def api_root():
	return {
		"config:": request.url + "config",
		"led_url": request.url + "led/( green | red )/",
		"led_url_POST": {"state":"(0 | 1)"}
	}


@app.route('/config/', methods=["GET"])
def get_config():
	global config
	r_configs = list()
	global rooms
	for r in rooms:
		room_config = { "room_name": r.name(),
				"room_gpio": r.pin(),
				"default_on": r.default(),
				"alarm_on": r.activated()}
		r_configs.append(room_config)
	
	config = {
		 "rooms" : r_configs,
		"all_disabled": bool(config["all_disabled"])
		}
	return config

@app.route('/setconfig/', methods=["GET","POST"])
def set_config():
	global config
	if request.method == "POST" and Util.check_config(request.data):
		config, _ = Util.harden_config_input(request.data)
		print(f"{datetime.now()}: update config")
		print(config)
		global rooms
		rooms=[]
		for r in config["rooms"]:
			rooms.append(Room(pin=r["room_gpio"], name=r["room_name"], default_on=r["default_on"], activated=r["alarm_on"]))
	return config

@app.route('/alarm/', methods=["GET"])
def api_alarm_control():
	check_alarm_state()
	return {"alarm_state": GPIO.input(LEDS["red"])}


@app.route('/led/<color>/', methods=["GET", "POST"])
def api_led_control(color):
	if request.method == "POST":
		if color in LEDS:
			GPIO.output(LEDS[color], int(request.data.get("state")))
	return {color: GPIO.input(LEDS[color])}


def check_alarm_state():
	get_config()
	global config
	if bool(config["all_disabled"]):
		Util.turn_led_on(LEDS["orange"])
	else:
		Util.turn_led_off(LEDS["orange"])
	all_ok = True
	all_closed = True
	for r in config["rooms"]:
		if not GPIO.input(r["room_gpio"]):
			all_closed = False
			Util.turn_led_off(LEDS["green"])
			if r["alarm_on"] and not config["all_disabled"]:
				print(f"{datetime.now()}: Alarm enabled and room {r['room_name']} open!")
				Util.turn_led_on(LEDS["red"])
				all_ok = False
	if all_ok:
		if all_closed:
			Util.turn_led_on(LEDS["green"])
		Util.turn_led_off(LEDS["red"])

def timer():
	check_alarm_state()
	threading.Timer(0.4, timer).start()


if __name__ == "__main__":
	app.run()

timer()

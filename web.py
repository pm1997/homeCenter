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
	LEDS = {"green": 16, "orange": 3, "red": 18}
	GPIO.setmode(GPIO.BOARD)
	for led in LEDS:
		print(led)
		GPIO.setup(LEDS[led], GPIO.OUT)

init_leds()

r1 = Room(40, "Bad")

rooms = [ r1 ]
config = {}
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
		"all_disabled": False
		}
	return config

@app.route('/setconfig/', methods=["GET","POST"])
def set_config():
	global config
	if request.method == "POST":
		config = request.data
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
	if config["all_disabled"]:
		print("all rooms disabled")
		Util.turn_led_on(LEDS["orange"])
	all_ok = True
	for r in config["rooms"]:
		if not GPIO.input(r["room_gpio"]):
			Util.turn_led_off(LEDS["green"])
			if r["alarm_on"] and not config["all_disabled"]:
				print(f"{datetime.now()}: Alarm enabled and room open!")
				Util.turn_led_on(LEDS["red"])
				all_ok = False
	if all_ok:
		Util.turn_led_on(LEDS["green"])
		Util.turn_led_off(LEDS["red"])

def timer():
	check_alarm_state()
	threading.Timer(0.4, timer).start()


if __name__ == "__main__":
	app.run()

timer()

#!/usr/bin/python

from flask import request
from flask_api import FlaskAPI
import RPi.GPIO as GPIO

import threading

from room import Room

LEDS = {"green": 16, "red": 18}
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LEDS["green"], GPIO.OUT)
GPIO.setup(LEDS["red"], GPIO.OUT)


r1 = Room(40, "Bad")

rooms = [ r1 ]


app = FlaskAPI(__name__)

@app.route('/', methods=["GET"])
def api_root():
	return {
		"config:": request.url + "config",
		"led_url": request.url + "led/( green | red )/",
		"led_url_POST": {"state":"(0 | 1)"}
	}


@app.route('/config/', methods=["GET"])
def show_config():
	r_configs = list()
	for r in rooms:
		room_config = { "room_name": r.name(),
				"room_gpio": r.pin(),
				"default_on": r.default(),
				"alarm_on": r.activate()}
		r_configs.append(room_config)
	return {
		 "rooms" : r_configs,
		"all_disabled": False
		}

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
	if r1.state() == 0 and GPIO.input(LEDS["red"]) == 0:
		GPIO.output(LEDS["red"], 1)
	elif r1.state() == 1 and GPIO.input(LEDS["red"]) == 1:
		GPIO.output(LEDS["red"], 0)

def timer():
	check_alarm_state()
	threading.Timer(0.4, timer).start()


if __name__ == "__main__":
	app.run()

timer()
#	app.run()

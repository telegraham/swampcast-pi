#!/usr/bin/python

import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import requests
import os

import logging
logging.basicConfig(filename='tempy.log',level=logging.WARNING,format='%(asctime)s %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')

auth_token = os.environ['AUTHORIZATION_TOKEN']

sensor = Adafruit_DHT.DHT22
pin = 4

def get_readings():
  humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
  return { "humidity": float(humidity), "temperature": float(temperature) }

def hit_api(dict):
  r = requests.post(url = "https://tempapi-backend.herokuapp.com/locations/turing/readings", 
                    params = dict,
                    headers = { "Authorization": auth_token })  

error_count = 0

def do_the_thing():
  global error_count
  logging.debug("starting...")
  while True:
    try:
      readings = get_readings()
      hit_api(readings)
      if error_count > 0:
        logging.warning("Successful fetch, resetting error count")
      error_count = 0
      time.sleep(5)
    except KeyboardInterrupt:
      logging.error("keyboard interrupt")
      GPIO.cleanup()
      print('bye')
      continue
    except Exception as e:
      logging.exception("error")
      error_count += 1
      logging.warning("{error_count} errors since last success".format(error_count=error_count))
      #print error_count
      if error_count > 100:
        logging.error("100+ errors, exiting")
        GPIO.cleanup()
        return
      sleep_timeout = 60 + 1.7 ** error_count
      logging.warning("sleeping {sleep_timeout}".format(sleep_timeout=sleep_timeout))
      time.sleep(sleep_timeout)

do_the_thing()


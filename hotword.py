#!/usr/bin/env python
# -*- coding: utf-8 -*-
# By Psychokiller1888

import json
import os.path
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import pytoml
import signal
import snowboydecoder
import logging
import sys
import os

# setup logger
logging.basicConfig(stream=sys.stderr, format='%(levelname)7s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


SNIPS_CONFIG_PATH = '/etc/snips.toml'

interrupted = False
siteId = 'default'
mqttServer = '127.0.0.1'
mqttPort = 1883
model = 'jarvis'
sensitivity = "0.8,0.80"
hotwordId = 'default'

def loadConfigs():
	global mqttServer, mqttPort, siteId, hotwordId

	if os.path.isfile(SNIPS_CONFIG_PATH):
		with open(SNIPS_CONFIG_PATH) as confFile:
			configs = pytoml.load(confFile)
			if 'mqtt' in configs['snips-common']:
				if ':' in configs['snips-common']['mqtt']:
					mqttServer = configs['snips-common']['mqtt'].split(':')[0]
					mqttPort = int(configs['snips-common']['mqtt'].split(':')[1])
				elif '@' in configs['snips-common']['mqtt']:
					mqttServer = configs['snips-common']['mqtt'].split('@')[0]
					mqttPort = int(configs['snips-common']['mqtt'].split('@')[1])
			if 'bind' in configs['snips-audio-server']:
				if ':' in configs['snips-audio-server']['bind']:
					siteId = configs['snips-audio-server']['bind'].split(':')[0]
				elif '@' in configs['snips-audio-server']['bind']:
					siteId = configs['snips-audio-server']['bind'].split('@')[0]
			if 'hotword_id' in configs['snips-hotword']:
				hotwordId = configs['snips-hotword']['hotword_id']
	else:
		logger.warning('Snips configs not found')

def signal_handler(signal, frame):
	global interrupted
	interrupted = True

def interrupt_callback():
	global interrupted
	return interrupted

def onHotword():
	global mqttServer, mqttPort, siteId
	publish.single('hermes/hotword/{0}/detected'.format(hotwordId), payload=json.dumps({'siteId': siteId, 'modelId': 'default'}), hostname=mqttServer, port=1883)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
	loadConfigs()
	detector = snowboydecoder.HotwordDetector('{}.umdl'.format(model), sensitivity_str=sensitivity)
	logger.info('Listening...')
	detector.start(detected_callback=onHotword, interrupt_check=interrupt_callback, sleep_time=0.03)
	detector.terminate()

#!/usr/bin/python2
# 
# Simple nagios plugin to check temperature and humidity
# with a DHT22 one wire bus sensor or similar. 
# Basically it only calls the Adafruit DHT driver and reads
# out the values.
# You can get the Adafruit DHT driver at GitHub:
# https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code
# 
# TODO: Use the nagios threshold syntax to make full use
# of the warning and critical thresholds.

import re
import subprocess
import time
import sys
import argparse

def main():
	
	parser = argparse.ArgumentParser(description = 'Nagios plugin to check DHT sensors using Adafruit DHT driver')
	parser.add_argument('-s', '--sensor', required=False, help='Sensor to use (supported sensors: 11, 22, 2302)', default='22')
	parser.add_argument('-p', '--pin', required=False, help='GPIO pin number (example: -p 4)', default='4')
	parser.add_argument('-w', '--warning', required=False, help='warning threshold for temperature and humidity (example: -w 25,80)', default='25,80')
	parser.add_argument('-c', '--critical', required=False, help='warning threshold for temperature and humidity (example: -c 30,85)', default='30,85')
	args = parser.parse_args()

	sensor = args.sensor
	pin = args.pin
	warningTemp = args.warning.split(',')[0]
	warningHum = args.warning.split(',')[1]
	criticalTemp = args.critical.split(',')[0]
	criticalHum = args.critical.split(',')[1]


	if sensor not in ['11', '22', '2302']:
		exitCheck(3, 'please select valid sensor (11, 22 or 2302)')

	# We need this try counter because the sensor sometimes doesn't deliver data.
	maxTries = 3
	tryCounter = 0
	while tryCounter < maxTries:
		try:
			temphum = subprocess.Popen(['timeout', '3s', 'Adafruit_DHT', sensor, pin], stdout=subprocess.PIPE).communicate()[0]
			temp = re.search('^Temp\s*=\s*(\d*\.\d)', temphum, re.M | re.S).group(1)
			hum = re.search('.*Hum\s*=\s*(\d*\.\d)', temphum, re.M | re.S).group(1)
			tryCounter = 100
		except AttributeError as e:
			tryCounter += 1
			time.sleep(5)
			

	if tryCounter == 100:
		msg = "Temperature: %s Humidity: %s | temp=%s;%s;%s hum=%s;%s;%s" % (temp, hum, temp, warningTemp, criticalTemp, hum, warningHum, criticalHum)
		if temp < warningTemp and hum < warningHum:
			status = 0
		elif temp < criticalTemp and hum < criticalHum:
			status = 1
		else:
			status = 2
		exitCheck(status, msg)	
	else:
		exitCheck(3, 'could not read temperature and humidity values')


def exitCheck(status, msg=''):
	if status == 0:
		msg = 'OK - ' + msg
	elif status == 1:
		msg = 'WARNING - ' + msg
	elif status == 2:
		msg = 'CRITICAL - ' + msg
	elif status == 3:
		msg = 'UNKNOWN - ' + msg
		
	print msg
	sys.exit(status)


if __name__ == '__main__':
	sys.exit(main())
#! /usr/bin/python

import serial
import cayenne.client as cayenne
import time
import urllib2
import os


e_wa = 0 # Enable workaround ?
wa_url = "" # url for work around

def save_csv(data):
	try:
		lines = "channel,data,dataType,dataUnits\n"
		if os.path.exists(str(data[0])+"_data.csv"):
			f = open(str(data[0])+"_data.csv", "r")
			lines = f.read()
			f.close()
		lines += str(data[0])+","+str(data[1][0])+","+str(data[1][1])+","+str(data[1][2])+"\n"
		f = open(str(data[0])+"_data.csv", "w")
		f.write(lines)
		f.close()
	except IndexError:
		pass

def on_message(message):
	print "Server Message: " + message

def serial_data(port, baud):
	ser = serial.Serial(port, baud, timeout=2)
	data = ser.readline()
	ser.close()
	return data

def on_connect(client,userdata,flags,rc):
	print "Connected with result code " + str(rc)

def get_mqtt_config():
	global e_wa, wa_url
	try:
		f = open("mqtt.conf", "r")
		config = f.read().split("\n")
		f.close()
		for i in range(0, len(config)):
			if "MQTT_PASSWORD" in config[i]:
				mqtt_password = config[i].split("=")[1]
			if "MQTT_USERNAME" in config[i]:
				mqtt_user = config[i].split("=")[1]
			if "CLIENT_ID" in config[i]:
				client_id = config[i].split("=")[1]
			if "MQTT_SERVER" in config[i]:
				mqtt_server = config[i].split("=")[1]
			if "MQTT_PORT" in config[i]:
				mqtt_port = config[i].split("=")[1]
			if "enable-workaround" in config[i]:
				e_wa = int(config[i].split("=")[1])
			if "workaround-url" in config[i]:
				wa_url = config[i].split("=")[1]
	except:
		print "ERROR: mqtt.config does not exist or cannot be accessed. Please run setup script."
	try:
		return mqtt_user, mqtt_password, client_id, mqtt_server, mqtt_port
	except:
		print "ERROR: Missing variables in config file. Please run setup script."
		return 0,0,0,0,0

def interpret_raw_data(data):
	# Modify this to model the data
	data_unit = "RAW" # change this to the unit.
	data_type = "Water_Level" # change this to whatever is being measured
	corrected_data = data # insert formula to correct data
	return corrected_data, data_type, data_unit
	
def send_via_work_around(channel, data, type, unit):
	login_detail = get_mqtt_config()
	url = wa_url + "?username=" + login_detail[0] + "&password=" + login_detail[1]
	url += "&client=" + login_detail[2] + "&channel=" + channel + "&data=" + data
	url += "&units=" + unit + "&type=" + type
	print url
	urllib2.urlopen(url) 

def process_data(data_string):
	global client
	data_array = data_string.split("\t")
	instrument_reading = []
	for i in range(0,len(data_array)):
		if "Instrument" in data_array[i]:
			instrument_reading.append(data_array[i].split(" ")[1])
		if "Reading" in data_array[i]:
			instrument_reading.append(interpret_raw_data(data_array[i].split(" ")[2].split("\r")[0]))
	try:
		if e_wa==0:
			client.virtualWrite(instrument_reading[0],instrument_reading[1][0],dataType=instrument_reading[1][1],dataUnit=instrument_reading[1][2])
		else:
			send_via_work_around(instrument_reading[0],instrument_reading[1][0],instrument_reading[1][1],instrument_reading[1][2])
	except IndexError:	
		pass
	save_csv(instrument_reading)
	print "sent data packet: " + str(instrument_reading)

# Start mqtt Client
time.sleep(10) # for auto start, wait for everything to connect.
login_detail = get_mqtt_config()
if e_wa == 0:
	client = cayenne.CayenneMQTTClient()
	client.on_connect = on_connect
	client.on_message = on_message
	client.begin(login_detail[0],login_detail[1],login_detail[2])
	client.virtualWrite("TESTING",23242)

while 1:
	data = serial_data("/dev/serial0", 2400)
	if e_wa == 0: client.loop()
	#client.virtualWrite("TESTING",23242)
	if data != "":
		process_data(data)


""" extract data from the IoT_MQTT_udp, transform to dataframe and save in a report """

import os, sys, logging, time, json, csv
import paho.mqtt.client as mqtt
from datetime import datetime


User = "assimilatus-grohuset-v3@ttn"
Password = "*****"
theRegion = "EU1"		

def saveToFile(json_file):
	end_device_ids = json_file["end_device_ids"]
	device_id = end_device_ids["device_id"]
	application_id = end_device_ids["application_ids"]["application_id"]
	received_at = json_file["received_at"]
	
	uplink_message = json_file["uplink_message"]
	f_port = uplink_message["f_port"]
	f_cnt = uplink_message["f_cnt"]
	frm_payload = uplink_message["frm_payload"]
	rssi = uplink_message["rx_metadata"][0]["rssi"]
	snr = uplink_message["rx_metadata"][0]["snr"]
	data_rate_index = uplink_message["settings"]["data_rate_index"]
	consumed_airtime = uplink_message["consumed_airtime"]
	
	# Daily log of uplinks
	now = datetime.now()
	pathNFile = now.strftime("%Y%m%d") + ".txt"
	print(pathNFile)
	if (not os.path.isfile(pathNFile)):
		with open(pathNFile, 'a', newline='') as tabFile:
			fw = csv.writer(tabFile, dialect='excel-tab')
			fw.writerow(["received_at", "application_id", "device_id", "f_port", "f_cnt", "frm_payload", "rssi", "snr", "data_rate_index", "consumed_airtime"])
	
	with open(pathNFile, 'a', newline='') as tabFile:
		fw = csv.writer(tabFile, dialect='excel-tab')
		fw.writerow([received_at, application_id, device_id, f_port, f_cnt, frm_payload, rssi, snr, data_rate_index, consumed_airtime])

	# Application log
	pathNFile = application_id + ".txt"
	print(pathNFile)
	if (not os.path.isfile(pathNFile)):
		with open(pathNFile, 'a', newline='') as tabFile:
			fw = csv.writer(tabFile, dialect='excel-tab')
			fw.writerow(["received_at", "device_id", "f_port", "f_cnt", "frm_payload", "rssi", "snr", "data_rate_index", "consumed_airtime"])

	with open(pathNFile, 'a', newline='') as tabFile:
		fw = csv.writer(tabFile, dialect='excel-tab')
		fw.writerow([received_at, device_id, f_port, f_cnt, frm_payload, rssi, snr, data_rate_index, consumed_airtime])

	# Device log
	pathNFile = application_id + "__" + device_id + ".txt"
	print(pathNFile)
	if (not os.path.isfile(pathNFile)):
		with open(pathNFile, 'a', newline='') as tabFile:
			fw = csv.writer(tabFile, dialect='excel-tab')
			fw.writerow(["received_at", "f_port", "f_cnt", "frm_payload", "rssi", "snr", "data_rate_index", "consumed_airtime"])

	with open(pathNFile, 'a', newline='') as tabFile:
		fw = csv.writer(tabFile, dialect='excel-tab')
		fw.writerow([received_at, f_port, f_cnt, frm_payload, rssi, snr, data_rate_index, consumed_airtime])


# MQTT events
def on_connect(mqttc, obj, flags, rc):
	print("\nConnect: rc = " + str(rc))

def on_subscribe(mqttc, obj, mid, granted_qos):
	print("\nSubscribe: " + str(mid) + " " + str(granted_qos))

def on_message(mqttc, obj, msg):
	print("\nMessage: " + msg.topic + " " + str(msg.qos)) # + " " + str(msg.payload))
	parsedJSON = json.loads(msg.payload)
	#print(json.dumps(parsedJSON, indent=4))	# Uncomment this to fill your terminal screen with JSON
	saveToFile(parsedJSON)

def on_log(mqttc, obj, level, string):
	print("\nLog: "+ string)
	logging_level = mqtt.LOGGING_LEVEL[level]
	logging.log(logging_level, string)



def main():
	mqttc = mqtt.Client()
	mqttc.on_connect = on_connect
	mqttc.on_subscribe = on_subscribe
	mqttc.on_message = on_message
	# mqttc.on_log = on_log		# Logging for debugging
	print("Connect")

	mqttc.username_pw_set(User, Password)

	# IMPORTANT - this enables the encryption of messages
	mqttc.tls_set()  # default certification authority of the system

	# mqttc.tls_set(ca_certs="mqtt-ca.pem") # Use this if you get security errors
	# It loads the TTI security certificate. Download it from their website from this page:
	# https://www.thethingsnetwork.org/docs/applications/mqtt/api/index.html
	# This is normally required if you are running the script on Windows!

	mqttc.connect(theRegion.lower() + ".cloud.thethings.network", 8883, 60)

	print("Subscribe")
	mqttc.subscribe("#", 0)
	print("And run forever")
	try:
		run = True
		while run:
			mqttc.loop(10)  # seconds timeout / blocking time
			print(".", end="", flush=True)  # feedback to the user that something is actually happening

	except KeyboardInterrupt:
		print("Exit")
		sys.exit(0)


if __name__ == '__main__':
	main()
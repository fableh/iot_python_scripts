import requests # http://docs.python-requests.org/en/master/
import psutil   # https://pypi.python.org/pypi/psutil
import time, sys, platform
import json
import base64
import re
from time import gmtime, strftime

import paho.mqtt.client as mqtt
# ========================================================================
def readsensors():
	global d_pctCPU
	global d_bootTime
	d_pctCPU = psutil.cpu_percent(percpu=False, interval = 1)
	d_bootTime=psutil.virtual_memory()
	print(d_bootTime.used)
	return

def on_connect_broker(client, userdata, flags, rc):
	print('Connected to MQTT broker with result code: ' + str(rc))

def on_subscribe(client, obj, message_id, granted_qos):
	print('on_subscribe - message_id: ' + str(message_id) + ' / qos: ' + str(granted_qos))

def on_message(client, obj, msg):
	# the msg, e.g. base64 encoded file content is often considerably large
	print('on_message - ' + msg.topic + ' ' + str(msg.qos))
	print('on_message - ' + msg.topic + ' ' + str(msg.qos) + ' ' + str(msg.payload))
	# parse the fields of the payload
	json_payload=json.loads(msg.payload)

	# capabilityId=json_payload['capabilityId']
	# print('capabilityId: ' + capabilityId)

	# downstream command handling
	if (re.match(r'.*"command":{"usage":"', str(msg.payload))):
		print('dealing with a control command')
		command=json_payload['command']
		print('command: ' + str(command))

		control_command=str(command['usage'])
		#control_arguments=str(command['arguments'])
		print("\n=======================NEW MQTT EVENT RCV======================================")
		print(control_command)
		print("=================================================================================")
		#print(control_arguments)

		# EXTENSION POINT
		# place additional activities, e.g. how to execute a specific command with its arguments here
		if (control_command == 'my_specific_command'):
			True
# ========================================================================

# read in configuration values from environment variables
config_broker='<host>'

config_credentials_key='./credentials.key'
config_credentials_crt='./credentials.crt'
#config_crt_4_landscape='./iotservice.cer'

config_alternate_id_device='<alternate_id_from_device>'
config_alternate_id_capability='<alternate_id_from_capability>'
config_alternate_id_sensor='<alternate_id_from_sensor>'

broker=config_broker
broker_port=8883

my_device=config_alternate_id_device
client=mqtt.Client(client_id=my_device)
client.on_connect=on_connect_broker
client.on_subscribe=on_subscribe
client.on_message=on_message


client.tls_set(ca_certs=None ,certfile=config_credentials_crt,  keyfile=config_credentials_key)

client.connect(broker, broker_port, 60)

my_publish_topic='measures/' + my_device
my_subscription_topic='commands/' + my_device
client.subscribe(my_subscription_topic, 0)

client.loop_start()

heartbeat_interval=5*6
try:
	while True:
		send_cpu=False
		#send_heartbeat=False
		readsensors()
		s_pctCPU = str(d_pctCPU)
		#d_tstamp = int(round(time.time()))
		#s_tstamp = str(d_tstamp)

		if send_cpu:
			time_string='GMT: ' + strftime('%Y-%m-%d %H:%M:%S', gmtime())
			my_mqtt_payload = "{ \"capabilityAlternateId\": \""+config_alternate_id_capability+"\",\"sensorAlternateId\": \""+config_alternate_id_sensor+"\", \"measures\":"+s_pctCPU+"}"

			print(my_mqtt_payload)
			result=client.publish(my_publish_topic, my_mqtt_payload, qos=0)
			print(result)

		time.sleep(heartbeat_interval)
		# print('in main loop')
		sys.stdout.flush()
except KeyboardInterrupt:
	print("Stopped by the user!")
 
import requests # http://docs.python-requests.org/en/master/
import psutil   # https://pypi.python.org/pypi/psutil
import time, sys, platform

hostiot4 ='<iot host>'


path = '/measures/<device alternate id>'
capabilityAltID='<capability alternate id>'
sensorAlternateId='<sensor alternate id>'


url = "https://"+hostiot4+path

def readsensors():
	global d_pctCPU
	global d_bootTime
	d_pctCPU = psutil.cpu_percent(percpu=False, interval = 1)
	d_bootTime=psutil.virtual_memory()
	print(d_bootTime.used)
	return

def postiotcf ():
	global d_pctCPU

	s_pctCPU = str(d_pctCPU)
	d_tstamp = int(round(time.time()))

	s_tstamp = str(d_tstamp)

	print("\nValues to post: ", d_pctCPU)
	payload = "{ \"capabilityAlternateId\": \""+capabilityAltID+"\",\"sensorAlternateId\": \""+sensorAlternateId+"\", \"measures\":"+s_pctCPU+"}"
	headers = {
			'content-type': "application/json",
			'cache-control': "no-cache"
			}

	print("Payload to post: ", payload)

	response = requests.request("POST", url, data=payload, headers=headers,cert=('./credentials.crt', './credentials.key'))

	print(response.status_code, response.text)

	return

try:
	while(True):
		
		readsensors()
		postiotcf()
		time.sleep(2)
except KeyboardInterrupt:
	print("Stopped by the user!")
 
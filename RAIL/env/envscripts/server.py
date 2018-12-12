# Remote Academy LabBox Environment
# Server Communication

from socketIO_client import SocketIO, BaseNamespace
import threading
import urllib.request
import urllib
import json
import time
import sys
import os
import logging
import base64
import shutil

from . import drivermanager
from .webcam import Webcam

LABBOX_IDENTIFIER = "rpi1"
DATA_PAUSE_TIME = 0.01
COLLECTING = False
RECORDING = False
CONNECTED = False

webSocket = None
wsChannel = None
gui = None
RALEConfig = None
driver = None
webcam = None
dataIndex = -1
curPinState = {}

class WebSocketHandler(BaseNamespace):
	def on_identify(self, data):
		def is_identified(data):
			global pwmPins
			if not 'errorCode' in data:
				if not RALEConfig.developmentMode:
					for key,inp in data.items():
						enable_gpio(inp["gpio"], inp["init"])
				set_state(True)
				runLoop()
			else:
				gui.infobox("LabBox Identification Failed!\n"+data['message'],
					title="ERROR",width=50,height=4)
		self.send("identity", LABBOX_IDENTIFIER, is_identified)
		
	def on_status(self, status):
		global COLLECTING
		global RECORDING
		global dataIndex
		if status == 2:
			COLLECTING = True
			RECORDING = True
		elif status == 1:
			COLLECTING = False
			RECORDING = True
		else:
			COLLECTING = False
			RECORDING = False
			dataIndex = -1
		collectData(not COLLECTING)
	
	def on_control(self, data):
		global pwmPins
		global dataIndex
		
		dataIndex = data["index"]
		inp = data["input"]
		if inp["mode"] != "pwm":
			set_gpio(inp["gpio"], inp["value"])

	def send(self,name,data,cb):
		try:
			wsChannel.emit(name,data,cb)
			webSocket.wait_for_callbacks(seconds=1)
			webSocket.wait()
		except:
			set_state(False)

def enable_gpio(pin,state):
	cmd = "gpio -g mode "+str(pin)+" out"
	os.system(cmd)
	set_gpio(pin,state)
	
def set_gpio(pin,state):
	global curPinState
	
	if pin in curPinState:
		if curPinState[pin] == state: return
		
	curPinState[pin] = state
		
	cmd = "gpio -g write "+str(pin)+" "+str(state)
	os.system(cmd)
	
def set_state(state):
	global CONNECTED
	if state != CONNECTED:
		CONNECTED = state
		stateString = "Connected"
		if not state:
			stateString = "Not Connected"
			
		gui.infobox("Connection State: %s\n\nLabBox Name: %s\nWebcam Name: %s" % (stateString, LABBOX_IDENTIFIER, webcam.getName()), 
						title="SYSTEM INFO", width=50, height=6)
		
		if not state:
			connectSocket()

def interface(_gui,_RALEConfig):
	global driver
	global webSocket
	global wsChannel
	global gui
	global RALEConfig
	global webcam
	
	# Set up module variables
	gui = _gui
	RALEConfig = _RALEConfig
	webcam = Webcam()
	webcam.powerOn()
	
	# Silence websocket logs
	logging.getLogger('requests').setLevel(logging.WARNING)
	logging.getLogger('past.translation').setLevel(logging.WARNING)
	logging.basicConfig(level=logging.CRITICAL)
	
	gui.infobox("Starting connection to Remote Academy...",title="PLEASE WAIT",width=50,height=4)
	driver = drivermanager.loadConfiguredDriver(RALEConfig)
	
	if driver == None:
		gui.infobox("No data collection equipment is configured!",title="ERROR",width=50,height=4)
		time.sleep(5)
		return
	else:
		driver.connect()
	
	connectSocket()
	
	while(True):
		pass
		
def connectSocket():
	global webSocket
	global wsChannel
	try:
		webSocket = SocketIO(RALEConfig.webSocketHostname, RALEConfig.webSocketPort)
		wsChannel = webSocket.define(WebSocketHandler, '/rale')
		webSocket.wait()
	except Exception as e:
		set_state(False)

def collectData(stop=False):
	global COLLECTING
	global driver
	
	if stop and COLLECTING:
		driver.stopRecordingData()
		COLLECTING = False
	elif not stop and not COLLECTING:
			COLLECTING = True
			driver.startRecordingData()
		
def sendData():
	global dataIndex
	
	if not CONNECTED:
		return
	try:
		if COLLECTING:
			data = json.dumps({"index":dataIndex,"data":driver.getCurrentDataSet()})
			wsChannel.emit("data",data)
		if RECORDING:
			image = base64.b64encode(webcam.getFrame()).decode("utf-8")
			wsChannel.emit("image",image)
	except:
		set_state(False)
		
def runLoop():
	while True:		
		sendData()
		
		# Read socket
		webSocket.wait(DATA_PAUSE_TIME)
# Remote Academy LabBox Environment
# Vernier LabPro Driver
# Implements http://www2.vernier.com/labpro/labpro_tech_manual.pdf
from enum import IntEnum

from .genericusb import GenericUSB

class LabPro(GenericUSB):
	driverName = "Vernier LabPro (USB)"
	
	def __init__(self):
		super(LabPro, self).__init__()
		self.vendorId = 0x08f7 
		self.productId = 0x0001
		self.channel = None
		self.digitalMode = None
	
	##### RALE Functions #####
	
	def startRecordingData(self):
		return self._startData()
		
	def stopRecordingData(self):
		return self._stopData()
		
	def getCurrentDataSet(self):
		return self._getData()
	
	def loadConfiguration(self, config):
		if config == None:
			return
		self.channel = LabPro.Channels[config["channel"]]
		self.digitalMode = LabPro.DigitalModes[config["digitalMode"]]
	
	def configureDriver(self, gui):
		channel = self.channel or LabPro.Channels.AnalogOne
		digitalMode = self.digitalMode or LabPro.DigitalModes.Sample
		
		while(True):
			code, tag = gui.menu("Vernier LabPro Configuration", choices=[
				("1", "Select Channel [Currently %s]" % channel.name),
				("2", "Select Digital Input Mode [Currently %s]" % digitalMode.name),
				("3", "Save Configuration")
			], extra_button=True, extra_label="Test Configuration")
			
			if code == gui.OK:
				if tag == "1":
					channel = self._configureEnum(gui, "Select Channel", LabPro.Channels) or channel
				if tag == "2":
					digitalMode = self._configureEnum(gui, "Select Digital Mode", LabPro.DigitalModes) or digitalMode
				if tag == "3":
					break
			elif code == gui.EXTRA:
				self._testConfiguration(gui,channel,digitalMode)
			else:
				return None
				
		return {"channel":channel.name,"digitalMode":digitalMode.name}
				
	def connect(self,noInit=False):
		super(LabPro, self).connect()
		if not noInit:
			self._initialize(self.channel, self.digitalMode)
	
	##### RALE Function Helpers #####
				
	def _configureEnum(self, gui, title, enum):
		options = enumerate(enum.__members__.items())
		choiceArray = []
		
		for index,option in options:
			choiceArray.append((str(index+1),option[0]))
		
		code, tag = gui.menu(title, choices=choiceArray)
		
		if code == gui.OK:
			return enum[choiceArray[int(tag)-1][1]]
		else:
			return None
			
	def _testConfiguration(self,gui,channel,digitalMode):
		gui.infobox("Connecting to LabPro...")
		self.connect(noInit=True)
		self._initialize(channel,digitalMode)
		self._startData()
		count = 0
		maxCount = 200
		
		gui.gauge_start("",title="Live LabPro Data", width=60, height=8)
		while(count < maxCount):
			data = self._getData()
			fieldA = data[0]
			fieldB = data[1] or 0.0
			gui.gauge_update(int((count/maxCount)*100),text="Data Field A| %f \nData Field B| %f" % (fieldA,fieldB),update_text=True)
			count = count+1
		self._stopData()
		gui.gauge_stop()
		
	
	##### High-Level Functionality #####
	
	def _initialize(self,channel,digitalMode=None):
		self.channel = channel
		self.digitalMode = digitalMode
		self._sendCommand(LabPro.Commands.Reset)
		self._sendCommand(LabPro.Commands.PowerControl, LabPro.PowerOptions.AlwaysOn)
		
		if channel >= LabPro.Channels.DigitalOne:
			# Digital requires dummy analog?!?!
			self._sendCommand(LabPro.Commands.ChannelSetup, LabPro.Channels.AnalogOne, 14)
			
			# Rotary Motion can get high resolution data with a special flag
			if digitalMode == LabPro.DigitalModes.RotaryMotion:
				self._sendCommand(LabPro.Commands.DigitalCapture, channel, digitalMode, 1)
			else:
				self._sendCommand(LabPro.Commands.DigitalCapture, channel, digitalMode)
		else:
			self._sendCommand(LabPro.Commands.ChannelSetup, channel)
	
	def _getCurrentSampleState(self):
		self._sendCommand(LabPro.Commands.SystemStatus)
		status = self._parseLabProArr(self._read())
		numSamples = int(status[9])
		state = int(status[13])
		return (state == 4,numSamples)
	
	def _getData(self):		
		if self.channel >= LabPro.Channels.DigitalOne:
			data = []
			
			# Get current sample number
			self._sendCommand(LabPro.Commands.DigitalCapture, self.channel, 0)
			sampleNum = (self._lastArrItem(self._parseLabProArr(self._read())[-1:]))
			
			# Get digital data record
			self._sendCommand(LabPro.Commands.DigitalCapture, self.channel, -1, sampleNum)
			data.append(self._lastArrItem(self._parseLabProArr(self._read())[-1:]))
			
			# Get additional digital data record if supported
			if self.digitalMode != LabPro.DigitalModes.Period and self.digitalMode != LabPro.DigitalModes.RotaryMotion:
				self._sendCommand(LabPro.Commands.DigitalCapture, self.channel, -2, sampleNum)
				data.append(self._lastArrItem(self._parseLabProArr(self._read())[-1:]))
			else:
				data.append(None)
			
			# Rotary Motion is giving high resolution 4x data. Account for this
			if self.digitalMode == LabPro.DigitalModes.RotaryMotion:
				data[0] = data[0]/4
				
			return data
		else:
			data = []
			
			self._sendCommand(LabPro.Commands.ChannelData, self.channel, 0)
			data.append(self._lastArrItem(self._parseLabProArr(self._read())))
			data.append(None)
			
			return data
	
	def _startData(self,timeBetweenSamples=0.10,numSamples=10000):		
		if self.channel >= LabPro.Channels.DigitalOne:
			self._sendCommand(LabPro.Commands.DataSetup, timeBetweenSamples, numSamples, 0)
			
	def _stopData(self):
		# System Setup does this??
		self._sendCommand(LabPro.Commands.SystemSetup, 0)
		
	def _testAudio(self):
		self.connect()
		self._sendCommand(LabPro.Commands.Sound, 50, 150)
		
	##### Low-level Communication Functions #####
	
	def _sendCommand(self, command, *parms):
		msg = "s{%d" % (command)
		for parm in parms:
			msg = msg + ",%f" % (parm)
		msg = msg + "}\n"
		return self._write(msg)
		
	def _read(self):
		readUSB = super(LabPro, self)._read
		data = []
		try:
			data = readUSB(timeout=500)
			while(1):
				data = data + readUSB(timeout=50)
		except:
			pass
		return ''.join([chr(x) for x in data])
		
	def _parseLabProArr(self, data):
		ret = []
		data = data.strip(" \t\n\r\x00").replace("{","").replace("}","")
		for item in data.split(","):
			if item.strip() == "":
				continue
			item = item.replace("\r","").replace("\n","").replace("\x00","").strip(" ").split(" ")[0]
			val = float(item)
			ret.append(val)
		return ret
	
	def _lastArrItem(self, arr):
		if len(arr)>0:
			return arr[-1]
		return 0
	
	##### LabPro Constants #####
	
	class Commands(IntEnum):
		Reset = 0
		ChannelSetup = 1
		DataSetup = 3
		DataControl = 5
		SystemSetup = 6
		SystemStatus = 7
		ChannelStatus = 8
		ChannelData = 9
		DigitalCapture = 12
		PowerControl = 102
		SetupInfo = 115
		GetSensorName = 116
		Sound = 1999
		
	class Channels(IntEnum):
		AnalogOne = 1
		AnalogTwo = 2
		AnalogThree = 3
		AnalogFour = 4
		DigitalOne = 41
		DigitalTwo = 42
		
	class DigitalModes(IntEnum):
		Sample = 1
		PulseWidth = 2
		PulseWidth2 = 3
		Period = 4
		Transitions = 5
		RotaryMotion = 6
		
	class PowerOptions(IntEnum):
		AlwaysOn = -1
		Normal = 0
		
# Remote Academy LabBox Environment
# Base Driver

class DeviceDriver:
	driverName = "Generic RALE Device Driver"
	
	def __init__(self):
		pass
	
	def canConnect(self):
		pass
	
	def connect(self):
		pass
		
	def loadConfiguration(self, config):
		pass
		
	def startRecordingData(self):
		pass
		
	def stopRecordingData(self):
		pass
		
	def getCurrentDataSet(self):
		pass
		
	def configureDriver(self, gui):
		gui.msgbox("This driver cannot be configured.")
				
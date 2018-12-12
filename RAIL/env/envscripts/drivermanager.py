# Remote Academy LabBox Environment
# Driver Manager

import pickle
import os

### Add new drivers here!
from .labpro import LabPro
drivers = [LabPro]

def validDrivers():
	valid = []
	for driver in drivers:
		instance = driver()
		if instance.canConnect():
			valid.append(driver)
	return valid
	
def getDriverFile(RALEConfig):
	if os.path.isfile(RALEConfig.driverFile):
		return pickle.load(open(RALEConfig.driverFile, "rb"))
	return None
	
def saveDriverConfiguration(driver, config, RALEConfig):
	if config == None:
		return
	pickle.dump({"driverName":driver.driverName,"config":config}, open(RALEConfig.driverFile, "wb"))
	
def loadDriverWithConfiguration(driverName, RALEConfig):
	driverInfo  = getDriverFile(RALEConfig)
	for driver in validDrivers():
		if driver.driverName == driverName:
			driverInstance = driver()
			
			if not driverInfo == None and driverName == driverInfo["driverName"]:
				driverInstance.loadConfiguration(driverInfo["config"])
				
			return driverInstance
	return None
	
def configureDriver(driver, gui, RALEConfig):
	driverInfo  = getDriverFile(RALEConfig)
	driverInstance = driver()
	
	if not driverInfo == None and driver.driverName == driverInfo["driverName"]:
		driverInstance.loadConfiguration(driverInfo["config"])
	
	saveDriverConfiguration(driver, driverInstance.configureDriver(gui), RALEConfig)
	
def loadConfiguredDriver(RALEConfig):
	driverInfo = getDriverFile(RALEConfig)
	if driverInfo == None:
		return None
	
	return loadDriverWithConfiguration(driverInfo["driverName"], RALEConfig)
		
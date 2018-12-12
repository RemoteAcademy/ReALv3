# Remote Academy LabBox Environment
# Main Menu

import time
import subprocess

from . import drivermanager
from . import server

def run(gui,RALEConfig):		
	code, tag = gui.menu("Main Menu", choices=[
		("1", "Connect to Remote Academy"),
		("2", "Configure Data Collection Equipment"),
		("3", "Restart LabBox")
	])
	
	if code == gui.OK:
		if tag == "1":
			server.interface(gui,RALEConfig)
		if tag == "2":
			configurator(gui,RALEConfig)
		if tag == "3":
			if not RALEConfig.developmentMode:
				gui.infobox("Restarting...")
				restart()

def restart():
	command = "/usr/bin/sudo /sbin/shutdown -r now"
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	
def configurator(gui,RALEConfig):
	gui.infobox("Autodetecting equipment...\nThis may take some time.")
	
	driverChoices = []
	drivers = drivermanager.validDrivers()
	for index,driver in enumerate(drivers):
		driverChoices.append((str(index+1),driver.driverName))
		
	if len(driverChoices) is 0:
		gui.msgbox("No equipment detected!", width=40, height=5)
	else:
		code, tag = gui.menu("I've found this equipment. Select one to configure.", choices=driverChoices)
		if code != gui.OK:
			return
			
		drivermanager.configureDriver(drivers[int(tag)-1], gui, RALEConfig)
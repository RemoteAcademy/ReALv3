# Remote Academy LabBox Environment
# Initialization Script

# All LabBoxes will download and run this script on boot
# One can assume the python dialog library is available on the system
# Additional python libraries can be named in PY_DEPS below. They will auto-download from pypi
# All necessary envscripts must be defined in RALE_DEPS to allow for auto-download

import time
import subprocess
import shutil
import os
import sys
import pip
import urllib.request
from dialog import Dialog

# Init Config
ENVSCRIPTS_FOLDER = os.path.expanduser("~/env/envscripts/")
REMOTEACADEMY_ENVFILES = "http://labbox-update.remote.academy/envscripts/"
RALE_DEPS = ["__init__.py","menu.py","drivermanager.py","devicedriver.py","genericusb.py","labpro.py","server.py","webcam.py"]
PY_DEPS = ["socketIO-client","v4l2","future"]

# Global Config
class RALEConfig:
	webSocketHostname = "sockets.remote.academy"
	webSocketPort = 8000
	developmentMode = (len(sys.argv) > 1 and sys.argv[1] == "devmode")
	configDirectory = os.path.expanduser("~/env/config/")
	driverFile = configDirectory+"driverConfig"
	
# Initialize RALE
def main():
	gui = Dialog(autowidgetsize=True)
	gui.set_background_title("Remote Academy LabBox Environment")
	error = None
	
	# Get Required Python Libraries
	gui.gauge_start("Updating base system...", width=50)
	error = download_pydependencies(gui, PY_DEPS)
	gui.gauge_stop()
	if error:
		gui.infobox(error)
		while(True):
			continue
	
	# Download and start RALE
	if not RALEConfig.developmentMode:
		gui.gauge_start("Downloading latest environment...", width=50)
		error = download_dependencies(gui, RALE_DEPS)
		gui.gauge_stop()
	else:
		gui.infobox("You're running RALE in development mode from local files.",title="NOTICE",width=50,height=4)
		time.sleep(1.5)
		
	if not os.path.isdir(RALEConfig.configDirectory):
		os.mkdir(RALEConfig.configDirectory)
	
	if not error:
		gui.infobox("Please wait... ",width=18,height=3)
		import envscripts.menu as MainMenu
		while(True):
			MainMenu.run(gui, RALEConfig)
	else:
		gui.infobox(error)
		while(True):
			continue
	
# Auto-update Helpers
def download_dependencies(gui,deps):
	if os.path.isdir(ENVSCRIPTS_FOLDER):
		shutil.rmtree(ENVSCRIPTS_FOLDER)
	os.mkdir(ENVSCRIPTS_FOLDER)
	lastUrl = ""
	try: 
		for idx,dep in enumerate(deps):
			lastUrl = REMOTEACADEMY_ENVFILES+dep
			urllib.request.urlretrieve(REMOTEACADEMY_ENVFILES+dep, ENVSCRIPTS_FOLDER+dep)
			gui.gauge_update(int(((idx+1)/len(deps))*100))
	except Exception as e:
		return str(e)+"\nOn URL: "+lastUrl
	return None
	
def download_pydependencies(gui,deps):
	try: 
		for idx,dep in enumerate(deps):
			code = pip.main(['install', '--user', '--quiet', dep])
			gui.gauge_update(int(((idx+1)/len(deps))*100))
			if code != 0: return "Could not update " + dep
	except Exception as e:
		return str(e)
	return None
	
def unlock_shell():
	os.system("mv ~/startup ~/startup.unlocked")
	os.exit() # Invalid on purpose

if __name__ == "__main__":
	main()
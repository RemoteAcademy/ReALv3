# Remote Academy LabBox Environment
# Generic USB Base Driver

import usb.core
import usb.util
from array import *

from .devicedriver import DeviceDriver

# A class to help build USB drivers for RALE
# Provides simple read and write functions for serial-like functionality
class GenericUSB(DeviceDriver):
	driverName = "Generic RALE Device Driver (USB)"
	
	def __init__(self):
		self.device = None
		self.vendorId = 0x0
		self.productId = 0x0
		self.rEndpoint = None
		self.wEndpoint = None
		
	def __del__(self):
		if not self.device is None:
			usb.util.dispose_resources(self.device)
	
	def canConnect(self):
		# Cast locate to boolean
		return not not self._locate()
	
	def connect(self):
		if not self.device is None and not self.wEndpoint is None and not self.rEndpoint is None:
			return True
			
		self.device = self._locate()
		if self.device is None:
			raise ValueError("USB Device Not Found")
		
		# Configure device
		self.device.set_configuration()
		intf = self.device.get_active_configuration()[(0,0)]
		self.wEndpoint = usb.util.find_descriptor(
			intf,
			custom_match = lambda e:
				usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
		)
		self.rEndpoint = usb.util.find_descriptor(
			intf,
			custom_match = lambda e:
				usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
		)
		return True
		
		
	### Internal Helpers ###
	### Use these in your drivers! ###
	def _locate(self):
		return usb.core.find(idVendor=self.vendorId,
			idProduct=self.productId)
			
	def _read(self,buf_size=64,timeout=100):
		return self.rEndpoint.read(buf_size,timeout)
		
	def _write(self,data):
		return self.wEndpoint.write(data)
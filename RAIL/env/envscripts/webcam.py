# Remote Academy LabBox Environment
# Webcam Wrapper

from past import autotranslate
autotranslate(['v4l2'])
import v4l2
import fcntl
import os
import mmap
import time
from io import StringIO

class Webcam:
	def __init__(self):
		self.available = False
		self.cp = None
		self.device = None
		self.fmt = None
		self.reqbuf = None
		self.imagebuffers = []
		
		try:
			fd = os.open('/dev/video0', os.O_RDWR)
			self.device = open(fd, 'wb+', buffering=0)
			
			self.available = True
			self.cp = v4l2.v4l2_capability()
			fcntl.ioctl(self.device, v4l2.VIDIOC_QUERYCAP, self.cp)
		except:
			pass
	
	def powerOn(self):
		self.setImageFormat()
		self.setUpBuffer()
		self.startStream()
	
	def powerOff(self):
		self.stopStream()
		
	def saveImage(self,location="/home/remote/Desktop/img.jpg"):
		with open(location, 'wb') as f:
			f.write(self.getFrame())
		print("Image saved to "+location)
		
	def setImageFormat(self):
		if not self.available: return
		self.fmt = v4l2.v4l2_format()
		self.fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
		self.fmt.fmt.pix.width = 160
		self.fmt.fmt.pix.height = 120
		self.fmt.fmt.pix.pixelformat = v4l2.V4L2_PIX_FMT_MJPEG
		self.fmt.fmt.pix.field = v4l2.V4L2_FIELD_NONE
		success = fcntl.ioctl(self.device, v4l2.VIDIOC_S_FMT, self.fmt)
		if success == -1:
			raise SystemError("Camera does not support image format!")
			
	def setUpBuffer(self):
		if not self.available: return
		if not self.fmt: raise SystemError("Image Format not set!")
		
		self.reqbuf = v4l2.v4l2_requestbuffers()
		self.reqbuf.count = 1
		self.reqbuf.type = self.fmt.type
		self.reqbuf.memory = v4l2.V4L2_MEMORY_MMAP
		
		success = fcntl.ioctl(self.device, v4l2.VIDIOC_REQBUFS, self.reqbuf)
		if success == -1:
			raise SystemError("Could not set up camera buffer")
			
		for index in range(self.reqbuf.count):
			buf = v4l2.v4l2_buffer()
			buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE 
			buf.memory = v4l2.V4L2_MEMORY_MMAP 
			buf.index = index 
			fcntl.ioctl(self.device, v4l2.VIDIOC_QUERYBUF, buf) 
			image = mmap.mmap(self.device.fileno(), buf.length, offset=buf.m.offset)
			self.imagebuffers.append(image)
			
		for index in range(self.reqbuf.count): 
			buf = v4l2.v4l2_buffer() 
			buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE 
			buf.memory = v4l2.V4L2_MEMORY_MMAP
			buf.index = index
			fcntl.ioctl(self.device, v4l2.VIDIOC_QBUF, buf)
	
	def startStream(self):
		if not self.available: return
		streamType = v4l2.v4l2_buf_type(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE) 
		fcntl.ioctl(self.device, v4l2.VIDIOC_STREAMON, streamType)
		
	def stopStream(self):
		if not self.available: return
		streamType = v4l2.v4l2_buf_type(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE)
		fcntl.ioctl(self.device, v4l2.VIDIOC_STREAMOFF, streamType)
		
	def getFrame(self):
		if not self.available: return
		buf = v4l2.v4l2_buffer() 
		buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE 
		buf.memory = v4l2.V4L2_MEMORY_MMAP 
		fcntl.ioctl(self.device, v4l2.VIDIOC_DQBUF, buf) 
		data = self.imagebuffers[buf.index].read(buf.bytesused)
		self.imagebuffers[buf.index].seek(0)
		fcntl.ioctl(self.device, v4l2.VIDIOC_QBUF, buf) 
		return self.addHuffman(data)

	def getName(self):
		if self.available:
			return self.cp.card.decode("utf-8")
		return "No Camera Detected"
		
	def addHuffman(self,data):
		huffman = \
            '\xFF\xC4\x01\xA2\x00\x00\x01\x05\x01\x01\x01\x01'\
            '\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02'\
            '\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x01\x00\x03'\
            '\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00'\
            '\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'\
            '\x0A\x0B\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05'\
            '\x05\x04\x04\x00\x00\x01\x7D\x01\x02\x03\x00\x04'\
            '\x11\x05\x12\x21\x31\x41\x06\x13\x51\x61\x07\x22'\
            '\x71\x14\x32\x81\x91\xA1\x08\x23\x42\xB1\xC1\x15'\
            '\x52\xD1\xF0\x24\x33\x62\x72\x82\x09\x0A\x16\x17'\
            '\x18\x19\x1A\x25\x26\x27\x28\x29\x2A\x34\x35\x36'\
            '\x37\x38\x39\x3A\x43\x44\x45\x46\x47\x48\x49\x4A'\
            '\x53\x54\x55\x56\x57\x58\x59\x5A\x63\x64\x65\x66'\
            '\x67\x68\x69\x6A\x73\x74\x75\x76\x77\x78\x79\x7A'\
            '\x83\x84\x85\x86\x87\x88\x89\x8A\x92\x93\x94\x95'\
            '\x96\x97\x98\x99\x9A\xA2\xA3\xA4\xA5\xA6\xA7\xA8'\
            '\xA9\xAA\xB2\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA\xC2'\
            '\xC3\xC4\xC5\xC6\xC7\xC8\xC9\xCA\xD2\xD3\xD4\xD5'\
            '\xD6\xD7\xD8\xD9\xDA\xE1\xE2\xE3\xE4\xE5\xE6\xE7'\
            '\xE8\xE9\xEA\xF1\xF2\xF3\xF4\xF5\xF6\xF7\xF8\xF9'\
            '\xFA\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05'\
            '\x04\x04\x00\x01\x02\x77\x00\x01\x02\x03\x11\x04'\
            '\x05\x21\x31\x06\x12\x41\x51\x07\x61\x71\x13\x22'\
            '\x32\x81\x08\x14\x42\x91\xA1\xB1\xC1\x09\x23\x33'\
            '\x52\xF0\x15\x62\x72\xD1\x0A\x16\x24\x34\xE1\x25'\
            '\xF1\x17\x18\x19\x1A\x26\x27\x28\x29\x2A\x35\x36'\
            '\x37\x38\x39\x3A\x43\x44\x45\x46\x47\x48\x49\x4A'\
            '\x53\x54\x55\x56\x57\x58\x59\x5A\x63\x64\x65\x66'\
            '\x67\x68\x69\x6A\x73\x74\x75\x76\x77\x78\x79\x7A'\
            '\x82\x83\x84\x85\x86\x87\x88\x89\x8A\x92\x93\x94'\
            '\x95\x96\x97\x98\x99\x9A\xA2\xA3\xA4\xA5\xA6\xA7'\
            '\xA8\xA9\xAA\xB2\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA'\
            '\xC2\xC3\xC4\xC5\xC6\xC7\xC8\xC9\xCA\xD2\xD3\xD4'\
            '\xD5\xD6\xD7\xD8\xD9\xDA\xE2\xE3\xE4\xE5\xE6\xE7'\
            '\xE8\xE9\xEA\xF2\xF3\xF4\xF5\xF6\xF7\xF8\xF9\xFA'
		instream = StringIO(data.decode('iso-8859-1'))
		outstream = StringIO()
		
		hdr = instream.read(2)
		outstream.write(hdr)
		
		foundHuffman = False
		while not foundHuffman:
			hdr = instream.read(4)
			
			if len(hdr) == 0:
				raise SystemError("Bad JPEG Format")			
			if hdr[0] != '\xff':
				raise SystemError("Bad JPEG Segment: " + header)
			if hdr[1] == '\xc4':
				foundHuffman = True
			elif hdr[1] == '\xda':
				break
			
			size = (ord(hdr[2]) << 8) + ord(hdr[3])
			outstream.write(hdr)
			outstream.write(instream.read(size-2))
		
		if not foundHuffman:
			outstream.write(huffman)
			outstream.write(hdr)
		
		outstream.write(instream.read())
		instream.close()
		outstream.flush()
		outstream.seek(0)
		return bytes(outstream.getvalue(), 'iso-8859-1')
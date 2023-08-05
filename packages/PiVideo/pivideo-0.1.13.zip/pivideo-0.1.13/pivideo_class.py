#!/usr/bin/python
######################################################################
#
#  PiVideo interface class
#  Copyright(c) 2018 by Lintest Systems LLC
#
######################################################################
#
#  Revision History
#	0.1.2	Initial Released Version
#	0.1.3	Serial port handling changed to support Raspberry Pi 3
#	0.1.4	Parameter processing bug fixed
#	0.1.5	Support for PiCapture HD1
#	0.1.6	Improved HD1 communications
#   0.1.8	No changes to interface class
#	0.1.9	Improved handling for communication errors in pivideo_class
#	0.1.10	Updated for Python3 compatibility; bug fix for "command"
#	0.1.11	Fix software update issue with Python3; Added custom EDID for HD1
#	0.1.12	Improved firmware update features; require future for Python 2
#	0.1.13	Fix for intermittent communications errors when PiCapture is searching for video
#
#  PiVideo Class:
#	open				Open a PiVideo object
#	pivideo_port		Specify the communications port - must match jumper settings
#	pivideo_i2c_address Specfiy the PiVideo I2C address - used with custom firmware
#	pivideo_serial_dev	Specify the Raspberry Pi serial device used for serial communication
#	ready				PiVideo processor is ready for the Raspberry Pi
#	running				Raspberry Pi camera interface is active
#	source				Video Source selection
#	active_source		Video source currently active
#	effect				Various video effects
#	led					Control status LEDs
#	lock				Active video status and type
#	config				Set or restore current configuration
#	version				Report the firmware version
#	long_version		Report the complete version information
#	id					Report the PiConfig hardware ID
#	update				Update the PiVideo processor firmware
#	command				Modify internal processing - use only with approved Lintest scripts
#	edid				Set the EDID block for the HD1; an empty block resets the HDMI connection to the source

from __future__ import print_function
from builtins import hex
from builtins import chr
from builtins import range
from builtins import object
try:
		import smbus
		_i2c_available = True
except:
		_i2c_available = False

import serial
import time

if __name__ == "__main__":
	print("pivideo_class.py contains the PiVideo class for use with pivideo.py or your program")

models=['SD1','HD1']
sources=['auto','video1','video2','video3','svideo','component','hdmi']
map_sources=['auto','video1','video2','video3','svideo','component','component','component','hdmi']
SD1_sources=['auto','video1','video2','video3','svideo','component']
HD1_sources=['auto','component','hdmi']
ports=['i2c0','i2c1','serial']
effects=['none','bw','colors','nomsg']
config_actions=['none','restore','save','reset']
led_settings=['normal','min','off']

class PiVideo(object):
	"""
	Provides a Python interface to the Lintest Systems PiCapture module
	"""

	detected_model = None				# SD1 or HD1
	status = None						# Changes to open port if successful
	port = "i2c1"						# Default communication port
	serial_device = "/dev/serial0"		# Default serial device
	i2c_address = 0x40					# 7 bit address (will be left shifted)
	serial_baudrates = [115200, 9600]
	serport = None
	ADV_versions = [0x03,0x1E]
	max_retries = 20
	comm_delay_i2c = 0.10
	comm_delay_serial = 0.02

#----------------------------------------------------------------------
# open

	def _get_open(self):
		if self.port in ports:
			if (self.port=="serial"):
				self.status=self._open_serial_port(self.serial_device)
			else:
				if (_i2c_available==True):
						self.status=self._open_i2c_port(self.port)
				else:
						raise PiVideoException("Python smbus module must be installed for I2C communication")
			if not self.status:
				raise PiVideoException("Unable to communicate with video processor")
			if (self.status in ports):
				if ((self._read_video_register(3) & 0x40)==0):
					self.detected_model = 'SD1'
				else:
					self.detected_model = 'HD1'
		else:
			raise PiVideoException("Bad communication port specified")
			self.status=None
		return self.status

	def _set_open(self,value):
		self._set_port(value)
		_get_open()


	open = property(_get_open, _set_open, doc="""
		Opens the communication port to the video processor.
		""" )

#----------------------------------------------------------------------
# model

	def _get_model(self):
		return self.detected_model

	def _set_model(self):
		raise PiVideoException("Model is read-only")

	model = property(_get_model,_set_model, doc="""
		PiCapture Model
		""" )


#----------------------------------------------------------------------
# version

	def _get_version(self):
		self._check_video_open()
		return format((self._read_video_register(4)&0x7F),'02X')
		
	def _set_version(self):
		raise PiVideoException("Version is read-only")

	version = property(_get_version,_set_version, doc="""
		Firmware version of the video processor
		""" )


#----------------------------------------------------------------------
# long_version

	def _get_long_version(self):
		self._check_video_open()
		return format(self._read_video_register(4),'02X')+format(self._read_video_register(3),'02X')+format(self._read_video_register(5),'02X')

	def _set_long_version(self):
		raise PiVideoException("Version is read-only")

	long_version = property(_get_long_version,_set_long_version, doc="""
		Complete Firmware version of the video processor
		""" )
#----------------------------------------------------------------------
# id

	def _get_id(self):
		self._check_video_open()
		idstring=""
		for r in range(30,38):
			idstring=format(self._read_video_register(r),'02X')+idstring
		return idstring

	def _set_id(self):
		raise PiVideoException("ID is read-only")

	id = property(_get_id,_set_id, doc="""
			Hardware ID of the video processor
			""" )

#----------------------------------------------------------------------
# update

	def _prepare_for_update(self):
		self._check_video_open()
		if (self.status == "serial"):
			self._write_serial_video_register(4,238)
			return 0
		elif (self.status == "loader"):
			self.serport.write("\x06")			
			return 0
		else:
			raise PiVideoException("Serial port not open for software update")
			return 1

	update = property(_prepare_for_update,_prepare_for_update, doc="""
		Place processor in firmware update mode
		""" )

#----------------------------------------------------------------------
# pivideo_port

	def _get_port(self):
		return self.port

	def _set_port(self, value):
		if value in ports:
			self.port=value
		else:
			raise PiVideoException("Bad communication port specified")
			self.port=None

	pivideo_port = property(_get_port, _set_port, doc="""
		Retrieves or sets the communication port used for the video processor.
		""" )

#----------------------------------------------------------------------
# pivideo_serial_dev

	def _get_serialdev(self):
		return self.serial_device

	def _set_serialdev(self, value):
		self.serial_device=value

	pivideo_serial_dev = property(_get_serialdev, _set_serialdev, doc="""
		Retrieves or sets the Raspberry Pi serial device used for the video processor.
		""" )

#----------------------------------------------------------------------
# pivideo_i2c_address

	def _get_i2caddr(self):
		return self.i2c_address

	def _set_i2caddr(self, value):
		self.i2c_address=value

	pivideo_i2c_address = property(_get_i2caddr, _set_i2caddr, doc="""
		Retrieves or sets the i2c address used for the video processor.
		""" )

#----------------------------------------------------------------------
# source

	def _get_source(self):
		self._check_video_open()
		return map_sources[self._read_video_register(6)]
	def _set_source(self, value):
		self._check_video_open()
		if 	(self.detected_model=='SD1'):
			if value in SD1_sources:
				source=value
				self._write_video_register(6,map_sources.index(source))
			else:
				raise PiVideoException("Bad SD1 source specified")
		else:
			if value in HD1_sources:
				source=value
				self._write_video_register(6,map_sources.index(source))
			else:
				raise PiVideoException("Bad HD1 source specified")		

	source = property(_get_source, _set_source, doc="""
		Retrieves or sets the desired video source.
		""" )

#----------------------------------------------------------------------
# active_source

	def _get_actsource(self):
		self._check_video_open()
		return map_sources[self._read_video_register(11)]
	def _set_actsource(self, value):
		_set_source(self,value)

	active_source = property(_get_actsource, _set_actsource, doc="""
		Retrieves or sets the desired video source.
		""" )


#----------------------------------------------------------------------
# effect

	def _get_effect(self):
		self._check_video_open()
		return effects[self._read_video_register(7)]
	def _set_effect(self, value):
		self._check_video_open()
		if value in effects:
			self._write_video_register(7,effects.index(value))
		else:
			raise PiVideoException("Bad effect specified")

	effect = property(_get_effect, _set_effect, doc="""
		Test modes and special effects
		""" )
		
#----------------------------------------------------------------------
# skip

	def _get_skip(self):
		self._check_video_open()
		if (self._read_video_register(13) == 0):
			return False
		else:
			return True
	def _set_skip(self, value):
		self._check_video_open()
		if value:
			self._write_video_register(13,1)
		else:
			self._write_video_register(13,0)

	skip = property(_get_skip, _set_skip, doc="""
		Enable frame skipping
		""" )
#----------------------------------------------------------------------
# ready

	def _get_ready(self):
		self._check_video_open()
		return self._read_video_register(8);

	def _set_ready(self):
		raise PiVideoException("Ready is read-only")

	ready = property(_get_ready,_set_ready, doc="""
		Video processor is ready
		""" )

#----------------------------------------------------------------------
# running

	def _get_running(self):
		self._check_video_open()
		return self._read_video_register(12)

	def _set_running(self):
		raise PiVideoException("Running is read-only")

	running = property(_get_running,_set_running, doc="""
		Raspberry Pi is accessing the camera port
		""" )

#----------------------------------------------------------------------
# lock

	def _get_lock(self):
		self._check_video_open()
		video_detected = self._read_video_register(9)
		if (self.model=='SD1'):
			if (video_detected==1):
				return 6
			elif (video_detected==2):
				return 6
			else:
				return 0
		elif (self.model=='HD1'):
			if (video_detected==1):
				return 6
			elif (video_detected==2):
				return 5
			elif (video_detected==3):
				return 1
			else:
				return 0
		else:
			return None

	def _set_lock(self):
		raise PiVideoException("Lock is read-only")

	lock = property(_get_lock,_set_lock, doc="""
		Video lock status:	matching camera mode for detected video 
		""" )

#----------------------------------------------------------------------
# config

	def _get_config(self):
		self._check_video_open()
		return self._read_video_register(6)

	def _set_config(self, value):
		self._check_video_open()
		if value in config_actions:
			action=value
			self._write_video_register(15,config_actions.index(action))
		else:
			raise PiVideoException("Bad configuration action specified")

	config = property(_get_config,_set_config, doc="""
		Configuration action:  1 = Restore, 2 = Save, 3 = Reset; Read returns source
		""" )

#----------------------------------------------------------------------
# led

	def _get_led(self):
		self._check_video_open()
		return led_settings[self._read_video_register(14)]
	def _set_led(self, value):
		self._check_video_open()
		if value in led_settings:
			self._write_video_register(14,led_settings.index(value))
		else:
			raise PiVideoException("Bad LED setting specified")

	led = property(_get_led, _set_led, doc="""
		LED Control
		""" )
		

#----------------------------------------------------------------------
# edid

	def _get_edid(self):
		raise PiVideoException("EDID can be assigned but not read")
		
	def _set_edid(self, value):
		self._check_video_open()
		if (self.model=='HD1'):
			if (len(value) == 256):
				self._write_video_register(70,0);
				for b in value:
					self._write_video_register(71,ord(b))
				self._write_video_register(72,0)
			elif (len(value) == 0):
				self._write_video_register(72,0)				
			else:
				raise PiVideoException("New EDID block must have 256 values")
		else:
			raise PiVideoException("EDID is only valid for PiCapture HD1")	

	edid = property(_get_edid, _set_edid, doc="""
		Set custom EDID block for HD1
		""" )


#----------------------------------------------------------------------
# command

	def _get_command(self):
		self._check_video_open()
		result=self._read_video_register(25)
		result=(result<<8)+self._read_video_register(24)
		result=(result<<8)+self._read_video_register(23)
		result=(result<<8)+self._read_video_register(22)
		return hex(result)

	def _set_command(self, value):
		self._check_video_open()
		if (self._read_video_register(16)==0):
			try:
				self._write_video_register(18,int(value[0:2],16))
				self._write_video_register(19,int(value[2:4],16))
				self._write_video_register(20,int(value[6:8],16))
				self._write_video_register(21,int(value[4:6],16))
				if (len(value)==16):
					self._write_video_register(22,int(value[14:16],16))
					self._write_video_register(23,int(value[12:14],16))
					self._write_video_register(24,int(value[10:12],16))
					self._write_video_register(25,int(value[8:10],16))
			except:
				raise PiVideoException("Invalid command string")
			else:
				if (len(value)==8):
					self._write_video_register(16,1)
				elif (len(value)==16):
					self._write_video_register(16,2)
				else:
					raise PiVideoException("Command must be 8 or 16 hex characters")
				result=1;
				while (result):
					result=self._read_video_register(16)
				result=self._read_video_register(17)
				return result
		else:
			raise PiVideoException("Video processor is busy - command not processed")

	command = property(_get_command,_set_command, doc="""
		Process command:  RESERVED
		""" )

#----------------------------------------------------------------------
# _open_i2c_port

	def _open_i2c_port(self,port_name):
		global video_i2c
		port_number=ports.index(port_name)
		if port_number < 2:
			try:
				video_i2c = smbus.SMBus(port_number)	# 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
			except:
				raise PiVideoException("Port not available - make sure it is enabled")
			else:
				retrycount = 0
				self.status=None
				while (retrycount < 4):		
					if	not self.status:
						try:
							video_i2c.write_quick(self.i2c_address)
						except IOError:
							self.status=None
						else:
							self.status=self.port
					retrycount+=1
				if not self.status:		
					raise PiVideoException("Video processor not found")
			return port_name
		else:
				raise PiVideoException("Illegal I2C Port Number")

#----------------------------------------------------------------------
# _open_serial_port

	def _open_serial_port(self,port_name):
		for speed in self.serial_baudrates:
			try:
				self.serport=serial.Serial(port_name,baudrate=speed,timeout=0.1)
				try:
					rval = self._read_serial_video_register(3)
					if (rval == 0x7E):
						self.detected_model = 'SD1'
						return "loader"
					elif (rval == 0xFE):
						self.detected_model = 'HD1'
						return "loader"
					elif ((rval & 0x80) > 0):
						try:
							if (self._read_serial_video_register(5) in self.ADV_versions):
								return "serial"
						except:
							pass
				except:
					pass
				self.serport.close();
			except:
				raise PiVideoException("Unable to open serial port")	
		return None		

#----------------------------------------------------------------------
	def _check_video_open(self):
		if not self.status:
			raise PiVideoException("Cannot communicate with video processor")
		
#----------------------------------------------------------------------
	def _write_i2c_video_register(self,address,value):
		retrycount = 0
		while (retrycount < self.max_retries):
			try:
				video_i2c.write_byte_data(self.i2c_address,address,value)
				return
			except IOError:
				retrycount+=1
				time.sleep(self.comm_delay_i2c)
		raise PiVideoException("Video processor communication error")			
		
#----------------------------------------------------------------------
	def _read_i2c_video_register(self,address):
		retrycount = 0
		while (retrycount < self.max_retries):
			try:
				video_i2c.write_byte(self.i2c_address,address)
				value=video_i2c.read_byte(self.i2c_address)
				return value
			except IOError:
				retrycount+=1
				time.sleep(self.comm_delay_i2c)
		raise PiVideoException("Video processor communication error")		
		
#----------------------------------------------------------------------
	def _clear_serial_buffer(self):
		lastchar=" "
		while (lastchar!=""):
			lastchar=self.serport.read(1)

#----------------------------------------------------------------------
	def _write_serial_video_register(self,address,value):
		self._clear_serial_buffer()
		retrycount = 0
		while (retrycount < self.max_retries):
			try:
				self.serport.write("\xDD")
				self.serport.write("\xDF")
				self.serport.write(chr(address))
				ch = chr(value)
				self.serport.write(ch.encode('latin-1'))
				return
			except IOError:
				retrycount+=1
				time.sleep(self.comm_delay_serial)
		raise PiVideoException("Video processor communication error")	
		
#----------------------------------------------------------------------
	def _read_serial_video_register(self,address):
		self._clear_serial_buffer()
		retrycount = 0
		while (retrycount < self.max_retries):
			try:
				self.serport.write("\xDD")
				self.serport.write("\xDE")
				self.serport.write(chr(address))
				time.sleep(self.comm_delay_serial)
				value=self.serport.read(1)	
				if (len(value)<1):
					retrycount+=1
				else:
					retrycount=10
					return ord(value)
			except IOError:
				retrycount+=1
				time.sleep(self.comm_delay_serial)
		raise PiVideoException("Video processor communication error")		

#----------------------------------------------------------------------
	def _write_video_register(self,address,value):
		if self.status:
			if (self.status=="serial"):
				self._write_serial_video_register(address,value)
			elif (self.status in ["i2c0","i2c1"]):
				self._write_i2c_video_register(address,value)
		
#----------------------------------------------------------------------
	def _read_video_register(self,address):
		if self.status:
			if (self.status=="serial"):
				return self._read_serial_video_register(address)
			elif (self.status in ["i2c0","i2c1"]):
				return self._read_i2c_video_register(address)
			else:
				return 0


#----------------------------------------------------------------------

class PiVideoException(Exception):
	pass

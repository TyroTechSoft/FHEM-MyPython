#!/usr/bin/env python3

#######################################################################################################################################
#                          
#  FHEM-MyPython                                                                                                    
#   98_WOLatDocker.py - V0.0.1
#    Date: 05.02.2023 - 09:25 Uhr
# 
#  by TyroTechSoft.de
#
#######################################################################################################################################
#
# WOLatDocker:				# Start WOL Devices
#			"98_WOLatDocker.py IP Port Protocol User Pass Device MAS"
#
##############
#
# IP			= IP from FHEM
# Port			= Port from FHEM
# Protocol		= Protocol from FHEM
# User			= User from FHEM
# Pass			= Pass From FHEM
# Device		= Device for response
# MAC			= WOL MAC
#
#######################################################################################################################################



##############################################################
### Imported Library

import fhem
import logging
import sys
import time
import json

from datetime import date, datetime
from wakeonlan import send_magic_packet


##############################################################
### Define System Variables

if __name__ == "__main__":
	MyVarSysArgs = sys.argv[1:]

try:
	MyVarSysData = {
		'IP': MyVarSysArgs[0],
		'Port': MyVarSysArgs[1],
		'Protocol': MyVarSysArgs[2],
		'User': MyVarSysArgs[3],
		'Pass': MyVarSysArgs[4],
		'Device': MyVarSysArgs[5],
		'MAC': MyVarSysArgs[6]}

except:
	print("WOLatDocker: No Args given!")
	

##############################################################
### Classes / Function

class MyClassSys:
	def __init__(self, MyVarSysData):
		self.AddReadings = ""
		self.Log = MyClassLog()
		self.TimeOut = 1

		logging.basicConfig()
		self.FHEM = fhem.Fhem(MyVarSysData['IP'], port=MyVarSysData['Port'], protocol=MyVarSysData['Protocol'], username=MyVarSysData['User'], password=MyVarSysData['Pass'])


	def AddReading(self, MyVarDevice, MyVarReading, MyVarValue):
		if self.AddReadings != "":
			self.AddReadings += ";"

		self.AddReadings += "setreading "+ self.DelSpace(MyVarDevice) +" "+ self.DelSpace(MyVarReading) +" "+ str(MyVarValue)


	def AddCMD(self, MyVarCMD):
		if self.AddReadings != "":
			self.AddReadings += ";"

		self.AddReadings += MyVarCMD


	def ExecuteReadings(self):
		if self.AddReadings != "":
			self.SetCMD(self.AddReadings)


	def GetReading(self, MyVarDevice, MyVarReading):
		return self.FHEM.get_device_reading(MyVarDevice, MyVarReading, value_only=True)


	def GetReadings(self, MyVarDevice):
		return self.FHEM.get_device_reading(MyVarDevice, value_only=True)


	def SetReading(self, MyVarDevice, MyVarReading, MyVarValue):
		self.FHEM.send_cmd("setreading "+ self.DelSpace(MyVarDevice) +" "+ self.DelSpace(MyVarReading) +" "+ str(MyVarValue), timeout=self.TimeOut)


	def SetCMD(self, MyCMD):
		self.FHEM.send_cmd(MyCMD, timeout=self.TimeOut)


	def DelSpace(self, MyVarString):
		return str(MyVarString).replace(" ", "").replace("-", "_")


class MyClassLog:
	def __init__(self):
		pass


##############################################################
### WOLatDocker Class

class WOLatDocker:
	def __init__(self, MyVarSysData):
		self.ClassSys = MyClassSys(MyVarSysData)
		MyVarDeviceName = MyVarSysData['Device']

		MyVarDeviceMAC = MyVarSysData['MAC'].replace(":", ".")

		send_magic_packet(MyVarDeviceMAC)


##############################################################
### Program

MyVarRun = WOLatDocker(MyVarSysData)
MyVarRun.ClassSys.ExecuteReadings()

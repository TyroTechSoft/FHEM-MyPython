#!/usr/bin/env python3

#######################################################################################################################################
#                          
#  FHEM-MyPython                                                                                                    
#   70_RepetierServer.py - V0.7
#    Date: 17.01.2020 - 07:16 Uhr
# 
#  by TyroTechSoft.de
#
#######################################################################################################################################
#
# RepetierServer:						# Get Data from Server
#			"70_RepetierServer.py IP Port Protocol User Pass TimeOut"
#
#######################################################################################################################################


##############################################################
### Imported Library

import fhem
import logging
import os
import sys
import json
import urllib.request
import time
import datetime

from pathlib import Path


##############################################################
### Classes / Function

class MyClassSys:
	def __init__(self, MyVarSysData):
		self.AddReadings = ""
		self.Log = MyClassLog()
		self.TimeOut = MyVarSysData['FHEM']['TimeOut']

		logging.basicConfig()
		self.FHEM = fhem.Fhem(MyVarSysData['FHEM']['IP'], port=MyVarSysData['FHEM']['Port'], protocol=MyVarSysData['FHEM']['Protocol'], username=MyVarSysData['FHEM']['User'], password=MyVarSysData['FHEM']['Pass'])


	def AddReading(self, MyVarDevice, MyVarReading, MyVarValue):
		if self.AddReadings != "":
			self.AddReadings += ";"

		self.AddReadings += "setreading " + MyVarDevice + " " + str(MyVarReading) + " " + str(MyVarValue)


	def GetReading(self, MyVarDevice, MyVarReading):
		return self.FHEM.get_device_reading(MyVarDevice, MyVarReading, value_only=True)


	def SetReading(self, MyCMD):
		self.FHEM.send_cmd(MyCMD, timeout = self.TimeOut)


class MyClassLog:
	def __init__(self):
		pass


##############################################################
### RepetierServer Class

class MyRepetierServerClass:
	def __init__(self, MyVarSysData):
		self.PrinterList = {}
		self.ClassSys = MyClassSys(MyVarSysData)

		for MyVarServer in self.ClassSys.FHEM.get(filters={'RS-Device': 'Server'}):
			try:
				self.GetServerInfo(MyVarServer)
				self.GetPrinterInfo(MyVarServer)
				self.GetPrinterData(MyVarServer)
			except:
				self.ClassSys.AddReading(MyVarServer['Name'], 'state', 'Offline')
				for MyVarPrinter in self.ClassSys.FHEM.get_readings(name=MyVarServer['Name'] + "..*", value_only=True):
					self.ClassSys.AddReading(MyVarPrinter, 'state', 'Offline')

		self.ClassSys.SetReading(self.ClassSys.AddReadings)


	def GetServerInfo(self, MyVarServer):
		with urllib.request.urlopen(MyVarServer['Attributes']['RS-Protocol'] + '://' + MyVarServer['Attributes']['RS-IP'] + ':' + str(MyVarServer['Attributes']['RS-Port']) + "/printer/info?apikey=" + MyVarServer['Attributes']['RS-Token'], timeout=5) as _MyVarRequest:
			MyVarData = json.loads(_MyVarRequest.read().decode())

			self.ClassSys.AddReading(MyVarServer['Name'], 'state', 'Online')
			self.ClassSys.AddReading(MyVarServer['Name'], 'Servername', MyVarData['servername'])
			self.ClassSys.AddReading(MyVarServer['Name'], 'Version', MyVarData['version'])
			self.ClassSys.AddReading(MyVarServer['Name'], 'Name', MyVarData['name'])

			for MyVarPrinter in MyVarData['printers']:
				if MyVarPrinter['online'] == 1:
					MyVarPrinter['online'] = "Online"
				else:
					MyVarPrinter['online'] = "Offline"

				self.ClassSys.AddReading(MyVarServer['Name'], MyVarPrinter['name'] + '_Name', MyVarPrinter['name'])
				self.ClassSys.AddReading(MyVarServer['Name'], MyVarPrinter['name'] + '_Active', MyVarPrinter['active'])
				self.ClassSys.AddReading(MyVarServer['Name'], MyVarPrinter['name'] + '_Online', MyVarPrinter['online'])
				self.ClassSys.AddReading(MyVarServer['Name'], MyVarPrinter['name'] + '_Slug', MyVarPrinter['slug'])


	def GetPrinterInfo(self, MyVarServer):
		with urllib.request.urlopen(MyVarServer['Attributes']['RS-Protocol'] + '://' + MyVarServer['Attributes']['RS-IP'] + ':' + str(MyVarServer['Attributes']['RS-Port']) + "/printer/list?apikey=" + MyVarServer['Attributes']['RS-Token'], timeout=5) as _MyVarRequest:
			for MyVarPrinter in json.loads(_MyVarRequest.read().decode())['data']:
				MyVarPrinterName = MyVarServer['Name'] + "." + MyVarPrinter['name']
				
				self.PrinterList[MyVarPrinter['slug']] = MyVarPrinterName
				
				if self.ClassSys.FHEM.get(name=MyVarPrinterName) == {}:
					self.ClassSys.FHEM.send_cmd("define " + MyVarServer['Name'] + "." + MyVarPrinter['name'] + " dummy;attr " + MyVarServer['Name'] + "." + MyVarPrinter['name'] + " group RepetierServer")

				if MyVarPrinter['job'] != "none":
					MyVarPrinter['online'] = "Printing"
				elif MyVarPrinter['online'] == 1:
					MyVarPrinter['online'] = "Online"
				else:
					MyVarPrinter['online'] = "Offline"

				MyVarLastState = self.ClassSys.GetReading(MyVarPrinterName, 'Online')

				if MyVarPrinter['online'] != MyVarLastState:
					if MyVarLastState == "Now Printing" and MyVarPrinter['online'] != "Printing":
						self.ClassSys.AddReading(MyVarPrinterName, 'state', 'Now ' + MyVarPrinter['online'] + ' End ' + self.ClassSys.GetReading(MyVarPrinterName, 'Job'))
					else:
						self.ClassSys.AddReading(MyVarPrinterName, 'state', 'Now ' + MyVarPrinter['online'])

				if MyVarPrinter['pauseState'] == 1:
					MyVarPrinter['pauseState'] = True
				else:
					MyVarPrinter['pauseState'] = False

				if MyVarPrinter['paused'] == 1:
					MyVarPrinter['paused'] = True
				else:
					MyVarPrinter['paused'] = False

				self.ClassSys.AddReading(MyVarPrinterName, 'Activ', MyVarPrinter['active'])
				self.ClassSys.AddReading(MyVarPrinterName, 'Job', MyVarPrinter['job'])
				self.ClassSys.AddReading(MyVarPrinterName, 'Name', MyVarPrinter['name'])
				self.ClassSys.AddReading(MyVarPrinterName, 'Online', MyVarPrinter['online'])
				self.ClassSys.AddReading(MyVarPrinterName, 'PauseState', MyVarPrinter['pauseState'])
				self.ClassSys.AddReading(MyVarPrinterName, 'Paused', MyVarPrinter['paused'])
				self.ClassSys.AddReading(MyVarPrinterName, 'Slug', MyVarPrinter['slug'])

				try:
					self.ClassSys.AddReading(MyVarPrinterName, 'Analysed', MyVarPrinter['analysed'])
					self.ClassSys.AddReading(MyVarPrinterName, 'Percent', round(MyVarPrinter['done'], 2))
					self.ClassSys.AddReading(MyVarPrinterName, 'JobID', MyVarPrinter['jobid'])
					self.ClassSys.AddReading(MyVarPrinterName, 'LinesSend', MyVarPrinter['linesSend'])
					self.ClassSys.AddReading(MyVarPrinterName, 'LinesTotal', MyVarPrinter['totalLines'])
					self.ClassSys.AddReading(MyVarPrinterName, 'LayerMax', MyVarPrinter['ofLayer'])
					self.ClassSys.AddReading(MyVarPrinterName, 'PrintStart', datetime.datetime.fromtimestamp(int(MyVarPrinter['printStart'])).strftime('%Y-%m-%d %H:%M:%S'))
					self.ClassSys.AddReading(MyVarPrinterName, 'PrintEnd', datetime.datetime.fromtimestamp(int(MyVarPrinter['printStart'] + MyVarPrinter['printTime'])).strftime('%Y-%m-%d %H:%M:%S'))
				except:
					self.ClassSys.AddReading(MyVarPrinterName, 'Analysed', 0)
					self.ClassSys.AddReading(MyVarPrinterName, 'Percent', 0)
					self.ClassSys.AddReading(MyVarPrinterName, 'JobID', 0)
					self.ClassSys.AddReading(MyVarPrinterName, 'LinesSend', 0)
					self.ClassSys.AddReading(MyVarPrinterName, 'LinesTotal', 0)
					self.ClassSys.AddReading(MyVarPrinterName, 'LayerMax', 0)
					self.ClassSys.AddReading(MyVarPrinterName, 'PrintStart', None)
					self.ClassSys.AddReading(MyVarPrinterName, 'PrintEnd', None)


	def GetPrinterData(self, MyVarServer):
		with urllib.request.urlopen(MyVarServer['Attributes']['RS-Protocol'] + '://' + MyVarServer['Attributes']['RS-IP'] + ':' + str(MyVarServer['Attributes']['RS-Port']) + "/printer/api?a=stateList&apikey=" + MyVarServer['Attributes']['RS-Token'], timeout=5) as _MyVarRequest:
			MyVarPrinters = json.loads(_MyVarRequest.read().decode())
			
			for MyVarPrinterKey in MyVarPrinters:
				MyVarDevice = self.PrinterList[MyVarPrinterKey]
				MyVarPrinter = MyVarPrinters[MyVarPrinterKey]
				
				self.ClassSys.AddReading(MyVarDevice, 'ExtruderActiv', MyVarPrinter['activeExtruder'])
				self.ClassSys.AddReading(MyVarDevice, 'DoorOpen', MyVarPrinter['doorOpen'])
				self.ClassSys.AddReading(MyVarDevice, 'FanFilter', MyVarPrinter['filterFan'])
				self.ClassSys.AddReading(MyVarDevice, 'Firmware', MyVarPrinter['firmware'])
				self.ClassSys.AddReading(MyVarDevice, 'FirmwareURL', MyVarPrinter['firmwareURL'])
				self.ClassSys.AddReading(MyVarDevice, 'FlowMultiply', MyVarPrinter['flowMultiply'])
				self.ClassSys.AddReading(MyVarDevice, 'HasXHome', MyVarPrinter['hasXHome'])
				self.ClassSys.AddReading(MyVarDevice, 'HasYHome', MyVarPrinter['hasYHome'])
				self.ClassSys.AddReading(MyVarDevice, 'HasZHome', MyVarPrinter['hasZHome'])
				self.ClassSys.AddReading(MyVarDevice, 'Layer', MyVarPrinter['layer'])
				self.ClassSys.AddReading(MyVarDevice, 'Lights', MyVarPrinter['lights'])
				self.ClassSys.AddReading(MyVarDevice, 'ExtruderCount', MyVarPrinter['numExtruder'])
				self.ClassSys.AddReading(MyVarDevice, 'PowerOn', MyVarPrinter['powerOn'])
				self.ClassSys.AddReading(MyVarDevice, 'Record', MyVarPrinter['rec'])
				self.ClassSys.AddReading(MyVarDevice, 'SDCardMounted', MyVarPrinter['sdcardMounted'])
				self.ClassSys.AddReading(MyVarDevice, 'ShutdownAfterPrint', MyVarPrinter['shutdownAfterPrint'])
				self.ClassSys.AddReading(MyVarDevice, 'SpeedMultiply', MyVarPrinter['speedMultiply'])
				self.ClassSys.AddReading(MyVarDevice, 'Volumetric', MyVarPrinter['volumetric'])
				self.ClassSys.AddReading(MyVarDevice, 'X', round(MyVarPrinter['x'], 3))
				self.ClassSys.AddReading(MyVarDevice, 'Y', round(MyVarPrinter['y'], 3))
				self.ClassSys.AddReading(MyVarDevice, 'Z', round(MyVarPrinter['z'], 3))

				for MyVarKey in str(len(MyVarPrinter['extruder'])):
					MyVarKey = int(MyVarKey)-1
					MyVarKeyStr = str(MyVarKey)
					self.ClassSys.AddReading(MyVarDevice, 'E' + MyVarKeyStr + 'Error', MyVarPrinter['extruder'][MyVarKey]['error'])
					self.ClassSys.AddReading(MyVarDevice, 'E' + MyVarKeyStr + 'TempGet', round(MyVarPrinter['extruder'][MyVarKey]['tempRead'], 2))
					self.ClassSys.AddReading(MyVarDevice, 'E' + MyVarKeyStr + 'TempSet', round(MyVarPrinter['extruder'][MyVarKey]['tempSet'], 2))
				
				for MyVarKey in str(len(MyVarPrinter['heatedBeds'])):
					MyVarKey = int(MyVarKey)-1
					MyVarKeyStr = str(MyVarKey)
					self.ClassSys.AddReading(MyVarDevice, 'B' + MyVarKeyStr + 'Error', MyVarPrinter['heatedBeds'][MyVarKey]['error'])
					self.ClassSys.AddReading(MyVarDevice, 'B' + MyVarKeyStr + 'TempGet', round(MyVarPrinter['heatedBeds'][MyVarKey]['tempRead'], 2))
					self.ClassSys.AddReading(MyVarDevice, 'B' + MyVarKeyStr + 'TempSet', round(MyVarPrinter['heatedBeds'][MyVarKey]['tempSet'], 2))
					self.ClassSys.AddReading(MyVarDevice, 'B' + MyVarKeyStr + 'OutPut', round(MyVarPrinter['heatedBeds'][MyVarKey]['output'], 2))
				
				for MyVarKey in str(len(MyVarPrinter['fans'])):
					MyVarKey = int(MyVarKey)-1
					MyVarKeyStr = str(MyVarKey)
					self.ClassSys.AddReading(MyVarDevice, 'F' + MyVarKeyStr + 'Activ', MyVarPrinter['fans'][MyVarKey]['on'])
					self.ClassSys.AddReading(MyVarDevice, 'F' + MyVarKeyStr + 'PWM', MyVarPrinter['fans'][MyVarKey]['voltage'])


##############################################################
### Define System Variables

if __name__ == "__main__":
	MyVarSysArgs = sys.argv[1:]

try:
	if MyVarSysArgs[0] != "":
		pass
except:
	MyVarSysArgs = {0: 'NoArgs'}


##############################################################
### Program

if MyVarSysArgs[0] == "NoArgs":
	print("RepetierServer: No Args given!")
else:
	MyVarSysData = {
		'Path': 'FHEM/MyPython/',
		'FHEM': {
			'IP': str(MyVarSysArgs[0]),
			'Port': str(MyVarSysArgs[1]),
			'Protocol': str(MyVarSysArgs[2]),
			'User': str(MyVarSysArgs[3]),
			'Pass': str(MyVarSysArgs[4]),
			'TimeOut': int(MyVarSysArgs[5])
			}
		}
	MyVarRun = MyRepetierServerClass(MyVarSysData)
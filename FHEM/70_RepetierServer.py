#!/usr/bin/env python3

#######################################################################################################################################
#                          
#  FHEM-MyPython                                                                                                    
#   70_RepetierServer.py - V0.8.7 - VersionsID 3
#    Date: 24.01.2020 - 12:19 Uhr
# 
#  by TyroTechSoft.de
#
#######################################################################################################################################
#
# RepetierServer:						# Get Data from Server
#			"70_RepetierServer.py IP Port Protocol User Pass TimeOut"
#
# RepetierServer:						# Send Printer CMD
#			"70_RepetierServer.py IP Port Protocol User Pass TimeOut Device Typ CMD"
#
##############
#
# IP				= IP from FHEM
# Port			= Port from FHEM
# Protocol	= Protocol from FHEM
# User			= User from FHEM
# Pass			= Pass From FHEM
# TimeOut		= TimeOut from FHEM
# Device		= Device that is using the CMD
# TYP				= Witch Typ of CMD (GCode / CMD / Coordinate) [Coordinate Check the Reading "HasHome XYZ" is it False, he do Homing]
# CMD				= Sends the CMD for the Typ
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
import urllib

from pathlib import Path


##############################################################
### Define System Variables

MyVarVersionID = 3

if __name__ == "__main__":
	MyVarSysArgs = sys.argv[1:]

try:
	MyVarSysDataFHEM = {
		'IP': MyVarSysArgs[0],
		'Port': MyVarSysArgs[1],
		'Protocol': MyVarSysArgs[2],
		'User': MyVarSysArgs[3],
		'Pass': MyVarSysArgs[4],
		'TimeOut': MyVarSysArgs[5]}

	try:
		MyVarSysDataCMD = {
			'Device': MyVarSysArgs[6],
			'Typ': MyVarSysArgs[7],
			'CMD': ''}

		for MyVarParm in MyVarSysArgs[8:]:
			if MyVarSysDataCMD['CMD'] != "":
				MyVarSysDataCMD['CMD'] += " "
			MyVarSysDataCMD['CMD'] += MyVarParm
		
	except:
		MyVarSysDataCMD = {
			'Device': '',
			'Typ': '',
			'CMD': ''}
except:
	MyVarSysArgs = {0: 'NoArgs'}

if MyVarSysArgs[0] == "NoArgs":
	print("RepetierServer: No Args given!")
else:
	MyVarSysData = {
		'Path': 'FHEM/MyPython/',
		'VID': MyVarVersionID,
		'Control': MyVarSysDataCMD,
		'FHEM': MyVarSysDataFHEM}


##############################################################
### Classes / Function

class MyClassSys:
	def __init__(self, MyVarSysData):
		self.AddReadings = ""
		self.Log = MyClassLog()
		self.TimeOut = int(MyVarSysData['FHEM']['TimeOut'])
		self.VersionID = MyVarSysData['VID']

		logging.basicConfig()
		self.FHEM = fhem.Fhem(MyVarSysData['FHEM']['IP'], port=MyVarSysData['FHEM']['Port'], protocol=MyVarSysData['FHEM']['Protocol'], username=MyVarSysData['FHEM']['User'], password=MyVarSysData['FHEM']['Pass'])


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
### RepetierServer Class

class MyRepetierServerClass:
	def __init__(self, MyVarSysData):
		self.PrinterList = {}
		self.ClassSys = MyClassSys(MyVarSysData)

		if MyVarSysData['Control']['Device'] != "" and MyVarSysData['Control']['Typ'] != "" and MyVarSysData['Control']['CMD'] != "":
			self.RunCMD(MyVarSysData)
		else:
			self.GetData()


	def CheckDeviceVersion(self, MyVarDevice, MyVarDeviceServer):
		try:
			MyVarVerionID = int(self.ClassSys.GetReading(MyVarDevice, "VersionID"))
		except:
			MyVarVerionID = 0

		MyVarCheckID = 1
		if MyVarVerionID < MyVarCheckID and self.ClassSys.VersionID >= MyVarCheckID:
			if MyVarDeviceServer == True:
				pass
			else:
				MyVarDefine = "define " + MyVarDevice + " dummy;"
				MyVarDefine += "attr " + MyVarDevice + " userattr RS-Device:Printer;"
				MyVarDefine += "attr " + MyVarDevice + " RS-Device Printer;"
				MyVarDefine += "attr " + MyVarDevice + " event-on-change-reading .*;"
				MyVarDefine += "attr " + MyVarDevice + " group RepetierServer;"
				MyVarDefine += "attr " + MyVarDevice + " event-on-change-reading .*"
				self.ClassSys.SetCMD(MyVarDefine)

		MyVarCheckID = 2
		if MyVarVerionID < MyVarCheckID and self.ClassSys.VersionID >= MyVarCheckID:
			if MyVarDeviceServer == True:
				pass
			else:
				self.ClassSys.SetCMD("attr " + MyVarDevice + " setList CMD:Home-All,Home-X,Home-Y,Home-Z")

		MyVarCheckID = 3
		if MyVarVerionID < MyVarCheckID and self.ClassSys.VersionID >= MyVarCheckID:
			if MyVarDeviceServer == True:
				pass
			else:
				self.ClassSys.SetCMD("attr " + MyVarDevice + " setList CMD:Home-All,Home-XY,Home-X,Home-Y,Home-Z GCode")

		MyVarCheckID = 4
		if MyVarVerionID < MyVarCheckID and self.ClassSys.VersionID >= MyVarCheckID:
			if MyVarDeviceServer == True:
				pass
			else:
				pass

		MyVarCheckID = 5
		if MyVarVerionID < MyVarCheckID and self.ClassSys.VersionID >= MyVarCheckID:
			if MyVarDeviceServer == True:
				pass
			else:
				pass

		self.ClassSys.AddReading(MyVarDevice, "VersionID", self.ClassSys.VersionID)


	def RunCMD(self, MyVarSysData):
		MyVarDeviceData = self.ClassSys.GetReadings(MyVarSysData['Control']['Device'])
		MyVarServer = self.ClassSys.FHEM.get(name=MyVarSysData['Control']['Device'].replace("." + MyVarDeviceData['Name'].replace(" ", "").replace("-", "_"), ""))
		MyVarSysData['Server'] = MyVarServer[0]
		MyVarSysData['Printer'] = MyVarDeviceData
		MyVarSysData['SendGcode'] = ""

		if MyVarDeviceData['Online'] == "Online":######################################################################################################################################################################################################################
			if MyVarSysData['Control']['Typ'] == "CMD":
				if MyVarSysData['Control']['CMD'] == "Home-All":
					MyVarSysData['SendGcode'] = {'Typ': 'cmd', 'CMD': 'G28'}
					self.RunCMDExecute(MyVarSysData)
				elif MyVarSysData['Control']['CMD'] == "Home-XY":
					MyVarSysData['SendGcode'] = {'Typ': 'cmd', 'CMD': 'G28 X Y'}
					self.RunCMDExecute(MyVarSysData)
				elif MyVarSysData['Control']['CMD'] == "Home-X":
					MyVarSysData['SendGcode'] = {'Typ': 'cmd', 'CMD': 'G28 X'}
					self.RunCMDExecute(MyVarSysData)
				elif MyVarSysData['Control']['CMD'] == "Home-Y":
					MyVarSysData['SendGcode'] = {'Typ': 'cmd', 'CMD': 'G28 Y'}
					self.RunCMDExecute(MyVarSysData)
				elif MyVarSysData['Control']['CMD'] == "Home-Z":
					MyVarSysData['SendGcode'] = {'Typ': 'cmd', 'CMD': 'G28 Z'}
					self.RunCMDExecute(MyVarSysData)

			elif MyVarSysData['Control']['Typ'] == "GCode":
				MyVarSysData['SendGcode'] = {'Typ': 'cmd', 'CMD': MyVarSysData['Control']['CMD']}
				self.RunCMDExecute(MyVarSysData)
			elif MyVarSysData['Control']['Typ'] == "Coordinate":
				for MyVarValue in MyVarSysData['Control']['CMD'].split(" "):

					if MyVarDeviceData['Has' + MyVarValue[0] + 'Home'] != "True":
						print("Ja")

					if MyVarValue[0] == "X":
						pass
					elif MyVarValue[0] == "Y":
						pass
					elif MyVarValue[0] == "Z":
						pass

					#print(MyVarValue[1:])

				self.ClassSys.AddReading(MyVarSysData['Control']['Device'], 'LastCMD', MyVarSysData['Control']['Typ'] + ": " + MyVarSysData['Control']['CMD'])
			else:
				self.ClassSys.AddReading(MyVarSysData['Control']['Device'], 'LastCMD', 'Unknown Command! ' + MyVarSysData['Control']['Typ'])
		elif MyVarDeviceData['Online'] == "Printing":
			self.ClassSys.AddReading(MyVarSysData['Control']['Device'], 'LastCMD', "Printer is Printing! Nothing done!")
		elif MyVarDeviceData['Online'] == "Offline":
			self.ClassSys.AddReading(MyVarSysData['Control']['Device'], 'LastCMD', "Printer is Offline! Nothing done!")


	def RunCMDExecute(self, MyVarSysData):
		MyVarUrl = MyVarSysData['Server']['Attributes']['RS-Protocol'] + '://' + MyVarSysData['Server']['Attributes']['RS-IP'] + ':' + str(MyVarSysData['Server']['Attributes']['RS-Port']) + "/printer/api/" + MyVarSysData['Printer']['Slug'] + "?a=send&data={\"" + MyVarSysData['SendGcode']['Typ'] + "\":\"" + MyVarSysData['SendGcode']['CMD'] + "\"}&apikey=" + MyVarSysData['Server']['Attributes']['RS-Token']
		MyVarSendCMD = urllib.request.urlopen(MyVarUrl.replace(" ", "%20"), timeout=5)
		#print(MyVarSendCMD.getcode())


	def GetData(self):
		for MyVarServer in self.ClassSys.FHEM.get(filters={'RS-Device': 'Server'}):
			try:
				self.GetDataInfoServer(MyVarServer)
				self.GetDataInfoPrinter(MyVarServer)
				self.ClassSys.AddReading(MyVarServer['Name'], 'RunState', 'OK!')
				self.ClassSys.AddReading(MyVarServer['Name'], 'state', 'Online')
			except:
				self.ClassSys.AddReading(MyVarServer['Name'], 'RunState', 'Can\'t Connect to Server!')
				self.ClassSys.AddReading(MyVarServer['Name'], 'state', 'Offline')
				
				for MyVarPrinter in self.ClassSys.FHEM.get_readings(name=MyVarServer['Name']+"..*"):
					self.ClassSys.AddReading(MyVarPrinter, 'state', 'Now Offline')
					self.ClassSys.AddReading(MyVarPrinter, 'Online', 'Offline')
				


	def GetDataInfoServer(self, MyVarServer):
		self.CheckDeviceVersion(MyVarServer['Name'], True)

		with urllib.request.urlopen(MyVarServer['Attributes']['RS-Protocol'] + '://' + MyVarServer['Attributes']['RS-IP'] + ':' + str(MyVarServer['Attributes']['RS-Port']) + "/printer/info?apikey=" + MyVarServer['Attributes']['RS-Token'], timeout=5) as _MyVarRequest:
			MyVarData = json.loads(_MyVarRequest.read().decode())
			
			self.ClassSys.AddReading(MyVarServer['Name'], 'state', 'Online')
			self.ClassSys.AddReading(MyVarServer['Name'], 'Servername', MyVarData['servername'])
			self.ClassSys.AddReading(MyVarServer['Name'], 'Version', MyVarData['version'])
			self.ClassSys.AddReading(MyVarServer['Name'], 'Name', MyVarData['name'])
			self.ClassSys.AddReading(MyVarServer['Name'], 'Printer_Count', len(MyVarData['printers']))

			for MyVarPrinter in MyVarData['printers']:
				if MyVarPrinter['online'] == 1:
					MyVarPrinter['online'] = "Online"
				else:
					MyVarPrinter['online'] = "Offline"

				self.ClassSys.AddReading(MyVarServer['Name'], 'Printer_' + MyVarPrinter['name'] + '_Name', MyVarPrinter['name'])
				self.ClassSys.AddReading(MyVarServer['Name'], 'Printer_' + MyVarPrinter['name'] + '_Active', MyVarPrinter['active'])
				self.ClassSys.AddReading(MyVarServer['Name'], 'Printer_' + MyVarPrinter['name'] + '_Online', MyVarPrinter['online'])
				self.ClassSys.AddReading(MyVarServer['Name'], 'Printer_' + MyVarPrinter['name'] + '_Slug', MyVarPrinter['slug'])


	def GetDataInfoPrinter(self, MyVarServer):
		with urllib.request.urlopen(MyVarServer['Attributes']['RS-Protocol'] + '://' + MyVarServer['Attributes']['RS-IP'] + ':' + str(MyVarServer['Attributes']['RS-Port']) + "/printer/list?apikey=" + MyVarServer['Attributes']['RS-Token'], timeout=5) as _MyVarRequest:
			for MyVarPrinter in json.loads(_MyVarRequest.read().decode())['data']:
				MyVarPrinterName = self.ClassSys.DelSpace(MyVarServer['Name'] + "." + MyVarPrinter['name'])
				self.PrinterList[MyVarPrinter['slug']] = MyVarPrinterName
				self.CheckDeviceVersion(MyVarPrinterName, False)

				self.ClassSys.AddReading(MyVarPrinterName, 'RS-Server', MyVarServer['Name'])

				if MyVarPrinter['job'] != "none":
					MyVarPrinter['online'] = "Printing"

					if self.ClassSys.GetReading(MyVarPrinterName, 'state') != "Now Printing":
						self.ClassSys.AddReading(MyVarPrinterName, 'state', 'Now Printing')
				elif MyVarPrinter['online'] == 1:
					MyVarPrinter['online'] = "Online"

					if self.ClassSys.GetReading(MyVarPrinterName, 'state') == "Now Printing":
						self.ClassSys.AddReading(MyVarPrinterName, 'JobLast', self.ClassSys.GetReading(MyVarPrinterName, 'Job'))
						self.ClassSys.AddReading(MyVarPrinterName, 'state', 'Now Printing Finish')
					elif self.ClassSys.GetReading(MyVarPrinterName, 'state') != "Now Online":
						self.ClassSys.AddReading(MyVarPrinterName, 'state', 'Now Online')
				else:
					MyVarPrinter['online'] = "Offline"

					if self.ClassSys.GetReading(MyVarPrinterName, 'state') != "Now Offline":
						self.ClassSys.AddReading(MyVarPrinterName, 'state', 'Now Offline')

				if MyVarPrinter['pauseState'] == 1:
					MyVarPrinter['pauseState'] = True
				else:
					MyVarPrinter['pauseState'] = False

				if MyVarPrinter['paused'] == 1:
					MyVarPrinter['paused'] = True
				else:
					MyVarPrinter['paused'] = False

				if MyVarPrinter['job'] == "None":
					MyVarPrinter['job'] = "None"

				self.ClassSys.AddReading(MyVarPrinterName, 'Connected2Server', MyVarServer['Name'])		
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

				MyVarCount = 0
				for MyVarKey in MyVarPrinter['extruder']:
					MyVarKeyStr = str(MyVarCount)
					self.ClassSys.AddReading(MyVarDevice, 'E' + MyVarKeyStr + 'Error', MyVarPrinter['extruder'][MyVarCount]['error'])
					self.ClassSys.AddReading(MyVarDevice, 'E' + MyVarKeyStr + 'TempGet', round(MyVarPrinter['extruder'][MyVarCount]['tempRead'], 2))
					self.ClassSys.AddReading(MyVarDevice, 'E' + MyVarKeyStr + 'TempSet', round(MyVarPrinter['extruder'][MyVarCount]['tempSet'], 2))
					MyVarCount += 1

				MyVarCount = 0
				for MyVarKey in str(len(MyVarPrinter['heatedBeds'])):
					MyVarKeyStr = str(MyVarCount)
					self.ClassSys.AddReading(MyVarDevice, 'B' + MyVarKeyStr + 'Error', MyVarPrinter['heatedBeds'][MyVarCount]['error'])
					self.ClassSys.AddReading(MyVarDevice, 'B' + MyVarKeyStr + 'TempGet', round(MyVarPrinter['heatedBeds'][MyVarCount]['tempRead'], 2))
					self.ClassSys.AddReading(MyVarDevice, 'B' + MyVarKeyStr + 'TempSet', round(MyVarPrinter['heatedBeds'][MyVarCount]['tempSet'], 2))
					self.ClassSys.AddReading(MyVarDevice, 'B' + MyVarKeyStr + 'OutPut', round(MyVarPrinter['heatedBeds'][MyVarCount]['output'], 2))
					MyVarCount += 1
				
				MyVarCount = 0
				for MyVarKey in str(len(MyVarPrinter['fans'])):
					MyVarKeyStr = str(MyVarCount)
					self.ClassSys.AddReading(MyVarDevice, 'F' + MyVarKeyStr + 'Activ', MyVarPrinter['fans'][MyVarCount]['on'])
					self.ClassSys.AddReading(MyVarDevice, 'F' + MyVarKeyStr + 'PWM', MyVarPrinter['fans'][MyVarCount]['voltage'])
					MyVarCount += 1


##############################################################
### Program

MyVarRun = MyRepetierServerClass(MyVarSysData)
MyVarRun.ClassSys.ExecuteReadings()
#!/usr/bin/env python3

#######################################################################################################################################
#                          
#  FHEM-MyPython                                                                                                    
#   98_PowerMessurement.py - V0.2.5
#    Date: 30.10.2021 - 12:47 Uhr
# 
#  by TyroTechSoft.de
#
#######################################################################################################################################
#
# BackUp:						# Upload BackUp File to FTP Server
#			"98_PowerMessurement.py IP Port Protocol User Pass Device"
#
##############
#
# IP				= IP from FHEM
# Port			= Port from FHEM
# Protocol	= Protocol from FHEM
# User			= User from FHEM
# Pass			= Pass From FHEM
# Device		= Device for response
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
		'Device': MyVarSysArgs[5]}

	try:
		MyVarSysData['DevicePrice'] = MyVarSysArgs[6]
	except:
		pass

except:
	print("PowerMessurement: No Args given!")
	

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
### PowerMessurement Class

class MyPowerMessurementClass:
	def __init__(self, MyVarSysData):
		self.ClassSys = MyClassSys(MyVarSysData)
		MyVarDate = str(datetime.now().strftime("%d.%m.%Y"))
		MyVarDeviceName = MyVarSysData['Device']
		MyVarPmArray = {}
		

		if MyVarDeviceName == "Set2Zero":
			MyVarDevice = self.ClassSys.FHEM.get(filters={'PmDevice': 'True'})
			MyVarDeviceName = MyVarDevice[0]['Name']
			MyVarDateReading = MyVarDevice[0]['Readings']['PmDate']['Value'].split(".")
			MyVarDateCurrent = MyVarDate.split(".")
			MyVarDateUpdate = False

			if MyVarDateReading[0] != MyVarDateCurrent[0]:
				self.ClassSys.AddReading(MyVarDeviceName, "PmToday", "0")
				self.ClassSys.AddReading(MyVarDeviceName, "PmYesterday", MyVarDevice[0]['Readings']['PmToday']['Value'])
				self.ClassSys.AddReading(MyVarDeviceName, "PmTodayCost", "0")
				self.ClassSys.AddReading(MyVarDeviceName, "PmYesterdayCost", MyVarDevice[0]['Readings']['PmTodayCost']['Value'])
				MyVarDateUpdate = True

			if MyVarDateReading[1] != MyVarDateCurrent[1]:
				self.ClassSys.AddReading(MyVarDeviceName, "PmMonth", "0")
				self.ClassSys.AddReading(MyVarDeviceName, "PmMonthLast", MyVarDevice[0]['Readings']['PmMonth']['Value'])
				
				self.ClassSys.AddReading(MyVarDeviceName, "PmMonthCost", "0")
				self.ClassSys.AddReading(MyVarDeviceName, "PmMonthLastCost", MyVarDevice[0]['Readings']['PmMonthCost']['Value'])
				MyVarDateUpdate = True

			if MyVarDateReading[2] != MyVarDateCurrent[2]:
				self.ClassSys.AddReading(MyVarDeviceName, "PmYear", "0")
				self.ClassSys.AddReading(MyVarDeviceName, "PmYearLast", MyVarDevice[0]['Readings']['PmYear']['Value'])
				
				self.ClassSys.AddReading(MyVarDeviceName, "PmYearCost", "0")
				self.ClassSys.AddReading(MyVarDeviceName, "PmYearLastCost", MyVarDevice[0]['Readings']['PmYearCost']['Value'])
				MyVarDateUpdate = True

			if MyVarDateUpdate == True:
				self.ClassSys.AddReading(MyVarDeviceName, "PmDate", MyVarDate)


		else:
			MyVarDeviceData = self.ClassSys.FHEM.get(name=MyVarDeviceName)
			MyVarPrice = self.ClassSys.GetReading(MyVarSysData['DevicePrice'], "Preis")

			if "PmTyp" not in MyVarDeviceData[0]['Attributes']:
				self.ClassSys.AddReading(MyVarDeviceName, "state", "Type of PowerMessurement not set!")
			elif "Tasmota" in MyVarDeviceData[0]['Attributes']['PmTyp']:
				if "Sensor" in MyVarDeviceData[0]['Readings']:
					MyVarDeviceData[0]['Readings']['Sensor']['Value'] = json.loads(MyVarDeviceData[0]['Readings']['Sensor']['Value'])
					MyVarPmData = self.TypTasmota(MyVarDeviceData[0])
					self.ClassSys.AddReading(MyVarDeviceName, "PmTotalOld", MyVarPmData['TotalOld'])
					self.ClassSys.AddReading(MyVarDeviceName, "PmTmtRestart", False)
				else:
					self.ClassSys.AddReading(MyVarDeviceName, "state", "No Reading Named \"Sensor\"!")
			elif "ESP-Easy" in MyVarDeviceData[0]['Attributes']['PmTyp']:
				MyVarPmData = self.TypESPEasy(MyVarDeviceData[0]['Readings'])
				if MyVarPmData['Error'] == True:
					self.ClassSys.AddReading(MyVarDeviceName, "State", "The Reading \"Count\" or \"Time\" not exist!")
				del MyVarPmData['Error']

			if "Voltage" in MyVarPmData:
				self.ClassSys.AddReading(MyVarDeviceName, "PmVoltage", MyVarPmData['Voltage'])

			MyVarCurPower = MyVarPmData['Power'] / 1000
			MyVarCurCount = MyVarPmData['Count'] / 1000
			MyVarCurPrice = MyVarCurCount * MyVarPrice

			if "PmInitial" not in MyVarDeviceData[0]['Readings']:
				self.ClassSys.AddReading(MyVarDeviceName, "PmInitial", "True")
				self.ClassSys.AddReading(MyVarDeviceName, "PmStart", MyVarDate)

				MyVarPmArray['PmToday'] = 0
				MyVarPmArray['PmYesterday'] = 0
				MyVarPmArray['PmMonth'] = 0
				MyVarPmArray['PmMonthLast'] = 0
				MyVarPmArray['PmYear'] = 0
				MyVarPmArray['PmYearLast'] = 0
				MyVarPmArray['PmTotal'] = 0

				MyVarPmArray['PmTodayCost'] = 0
				MyVarPmArray['PmYesterdayCost'] = 0
				MyVarPmArray['PmMonthCost'] = 0
				MyVarPmArray['PmMonthLastCost'] = 0
				MyVarPmArray['PmYearCost'] = 0
				MyVarPmArray['PmYearLastCost'] = 0
				MyVarPmArray['PmTotalCost'] = 0

				self.ClassSys.AddReading(MyVarDeviceName, "PmYesterday", MyVarPmArray['PmYesterday'])
				self.ClassSys.AddReading(MyVarDeviceName, "PmMonthLast", MyVarPmArray['PmMonthLast'])
				self.ClassSys.AddReading(MyVarDeviceName, "PmYearLast", MyVarPmArray['PmYearLast'])

				self.ClassSys.AddReading(MyVarDeviceName, "PmYesterdayCost", MyVarPmArray['PmYesterdayCost'])
				self.ClassSys.AddReading(MyVarDeviceName, "PmMonthLastCost", MyVarPmArray['PmMonthLastCost'])
				self.ClassSys.AddReading(MyVarDeviceName, "PmYearLastCost", MyVarPmArray['PmYearLastCost'])
			else:
				MyVarPmArray['PmToday'] = round(MyVarDeviceData[0]['Readings']['PmToday']['Value'] + MyVarCurCount,3)
				MyVarPmArray['PmMonth'] = round(MyVarDeviceData[0]['Readings']['PmMonth']['Value'] + MyVarCurCount,3)
				MyVarPmArray['PmYear'] = round(MyVarDeviceData[0]['Readings']['PmYear']['Value'] + MyVarCurCount,3)
				MyVarPmArray['PmTotal'] = round(MyVarDeviceData[0]['Readings']['PmTotal']['Value'] + MyVarCurCount,3)

				MyVarPmArray['PmTodayCost'] = round(MyVarDeviceData[0]['Readings']['PmTodayCost']['Value'] + MyVarCurPrice,7)
				MyVarPmArray['PmMonthCost'] = round(MyVarDeviceData[0]['Readings']['PmMonthCost']['Value'] + MyVarCurPrice,7)
				MyVarPmArray['PmYearCost'] = round(MyVarDeviceData[0]['Readings']['PmYearCost']['Value'] + MyVarCurPrice,7)
				MyVarPmArray['PmTotalCost'] = round(MyVarDeviceData[0]['Readings']['PmTotalCost']['Value'] + MyVarCurPrice,7)

			self.ClassSys.AddReading(MyVarDeviceName, "PmDate", MyVarDate)
			self.ClassSys.AddReading(MyVarDeviceName, "PmPower", MyVarCurPower)

			self.ClassSys.AddReading(MyVarDeviceName, "PmToday", MyVarPmArray['PmToday'])
			self.ClassSys.AddReading(MyVarDeviceName, "PmMonth", MyVarPmArray['PmMonth'])
			self.ClassSys.AddReading(MyVarDeviceName, "PmYear", MyVarPmArray['PmYear'])
			self.ClassSys.AddReading(MyVarDeviceName, "PmTotal", MyVarPmArray['PmTotal'])

			self.ClassSys.AddReading(MyVarDeviceName, "PmTodayCost", MyVarPmArray['PmTodayCost'])
			self.ClassSys.AddReading(MyVarDeviceName, "PmMonthCost", MyVarPmArray['PmMonthCost'])
			self.ClassSys.AddReading(MyVarDeviceName, "PmYearCost", MyVarPmArray['PmYearCost'])
			self.ClassSys.AddReading(MyVarDeviceName, "PmTotalCost", MyVarPmArray['PmTotalCost'])


	def TypTasmota(self, MyVarJsonSensor):
		MyVarArray = {}
		MyVarArray['Power'] = MyVarJsonSensor['Readings']['Sensor']['Value']['ENERGY']['Power']
		MyVarArray['Voltage'] = MyVarJsonSensor['Readings']['Sensor']['Value']['ENERGY']['Voltage']
		MyVarArray['TotalOld'] = round(MyVarJsonSensor['Readings']['Sensor']['Value']['ENERGY']['Total'] * 1000)

		if "PmTotalOld" not in MyVarJsonSensor['Readings'] or "PmTmtRestart" not in MyVarJsonSensor['Readings'] or MyVarJsonSensor['Readings']['PmTmtRestart']['Value'] == "True":
			MyVarArray['Count'] = 0
		else:
			MyVarArray['Count'] = MyVarArray['TotalOld'] - MyVarJsonSensor['Readings']['PmTotalOld']['Value']

		return MyVarArray


	def TypESPEasy(self, MyVarReadings):
		MyVarArray = {}
		MyVarArray['Error'] = False
		MyVarArray['Count'] = 0
		MyVarArray['Power'] = 0

		if "Count" not in MyVarReadings and "Time" not in MyVarReadings:
			MyVarArray['Error'] = True
		else:
			MyVarArray['Count'] = MyVarReadings['Count']['Value']
			MyVarArray['Power'] = round((1000 * (3.6 / int(MyVarReadings['Time']['Value']) * 1000) + 0.5) / 1000)

		return MyVarArray





##############################################################
### Program

MyVarRun = MyPowerMessurementClass(MyVarSysData)
MyVarRun.ClassSys.ExecuteReadings()

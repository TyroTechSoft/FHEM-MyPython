#!/usr/bin/env python3

#######################################################################################################################################
#                          
#  FHEM-MyPython                                                                                                    
#   98_WebSiteReader.py - V0.1.0
#    Date: 30.10.2021 - 05:28 Uhr
# 
#  by TyroTechSoft.de
#
#######################################################################################################################################
#
# WebSiteReader:				# Read Values from Website
#			"98_WebSiteReader.py IP Port Protocol User Pass Typ"
#
##############
#
# IP				= IP from FHEM
# Port			= Port from FHEM
# Protocol	= Protocol from FHEM
# User			= User from FHEM
# Pass			= Pass From FHEM
# Typ				= Typ of request
#
#######################################################################################################################################



##############################################################
### Imported Library

import fhem
import logging
import sys
import requests
import time

from bs4 import BeautifulSoup
from datetime import date


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
		'Typ': MyVarSysArgs[5]}

except:
	print("WebSiteReader: No Args given!")
	

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
### WebSiteReader Class

class MyWebSiteReaderClass:
	def __init__(self, MyVarSysData):
		self.ClassSys = MyClassSys(MyVarSysData)

		if(MyVarSysData['Typ'] == "CleverTanken"):
			self.CleverTanken()


	def CleverTanken(self):
		for MyVarDevice in self.ClassSys.FHEM.get(filters={'WSR-Device': 'CleverTanken'}):

			MyVarBeautifulSoup = BeautifulSoup(requests.get("https://www.clever-tanken.de/tankstelle_details/"+ str(MyVarDevice['Attributes']['WSR-ID'])).content, 'html.parser')
			MyVarKeys = MyVarBeautifulSoup.find_all("div", {"class" : "price-type-name"})
			MyVarCount = 0
			MyVarFuelList = ""
			MyVarTypArray = ""

			if "WSR-Typ" in MyVarDevice['Attributes']:
				MyVarTypArray = MyVarDevice['Attributes']['WSR-Typ'].split(",")

			while True:
				MyVarCount += 1

				try:
					MyVarKey = MyVarKeys[MyVarCount-1].get_text().replace(" ", "_")

					if MyVarKey in MyVarTypArray or MyVarTypArray == "":
						self.ClassSys.AddReading(MyVarDevice['Name'], MyVarKey, MyVarBeautifulSoup.find(id="current-price-"+ str(MyVarCount)).get_text() +"9")
				except:
					break


##############################################################
### Program

MyVarRun = MyWebSiteReaderClass(MyVarSysData)
MyVarRun.ClassSys.ExecuteReadings()

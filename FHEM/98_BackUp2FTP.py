#!/usr/bin/env python3

#######################################################################################################################################
#                          
#  FHEM-MyPython                                                                                                    
#   98_BackUp2FTP.py - V0.1.5
#    Date: 07.11.2021 - 11:56 Uhr
# 
#  by TyroTechSoft.de
#
#######################################################################################################################################
#
# BackUp:						# Upload BackUp File to FTP Server
#			"98_BackUp2FTP.py IP Port Protocol User Pass Device"
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
import os
import glob
import ntpath
import json
import sys
import ssl

from datetime import date, datetime
from ftplib import FTP_TLS, FTP


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

except:
	print("BackUp2FTP: No Args given!")


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
### Back2FTP Class

class MyBack2FTPClass:
	def __init__(self, MyVarSysData):
		self.ClassSys = MyClassSys(MyVarSysData)
		self.DateTime = str(datetime.now().strftime("%d.%m.%Y %H:%M"))
		self.Device = MyVarSysData['Device']
		MyVarDeviceData = self.ClassSys.FHEM.get(name=self.Device)

		self.ClassSys.SetReading(self.Device, 'state', 'Running')

		self.Data = {
		'IP': MyVarDeviceData[0]['Attributes']['BU-HostFTP'],
		'User': MyVarDeviceData[0]['Attributes']['BU-UserFTP'],
		'Pass': MyVarDeviceData[0]['Attributes']['BU-PassFTP'],
		'MaxFile': {
			'FHEM': MyVarDeviceData[0]['Attributes']['BU-MaxFileFHEM'],
			'FTP': MyVarDeviceData[0]['Attributes']['BU-MaxFileFTP']},
		'Dir': {
			'FHEM': MyVarDeviceData[0]['Attributes']['BU-DirFHEM'],
			'FTP': MyVarDeviceData[0]['Attributes']['BU-DirFTP']}}

		try:
			os.chdir(self.Data['Dir']['FHEM'])
		except:
			self.ClassSys.SetReading(self.Device, 'state', 'FHEM Error: Cannot find or access FHEM Dir!')
			print("FHEM Error: Cannot find or access FHEM Dir!")
			exit()


########### FTP Connect

		try:
			try:
				self.FTP = FTP_TLS(host= self.Data['IP'], user= self.Data['User'], passwd= self.Data['Pass'])
				self.FTP.ssl_version = ssl.PROTOCOL_SSLv23
			except:
				self.FTP = FTP(host= self.Data['IP'], user= self.Data['User'], passwd= self.Data['Pass'])

			self.FTP.cwd(self.Data['Dir']['FTP'])
			self.FTP.encoding = "utf-8"

		except:
			self.ClassSys.SetReading(self.Device, 'state', 'FTP Error: Cannot connect!')
			print("BackUp2FTP: FTP Error: Cannot connect!")
			exit()


########### Upload File

		MyVarFile = max(glob.iglob(self.Data['Dir']['FHEM'] + '/*'), key=os.path.getctime)
		MyVarFileName = ntpath.basename(MyVarFile)
		self.ClassSys.SetReading(self.Device, 'FileName', MyVarFileName)

		with open(MyVarFileName, 'rb') as MyVarUpload:
			self.FTP.storbinary('STOR ' + ntpath.basename(MyVarFileName), MyVarUpload)


########### Delete old Files

		while True:
			MyVarBackUpListFHEM = os.listdir(self.Data['Dir']['FHEM'])

			if len(MyVarBackUpListFHEM) > self.Data['MaxFile']['FHEM']:
				os.remove(os.path.abspath(self.Data['Dir']['FHEM'] + "/" + min(MyVarBackUpListFHEM, key= os.path.getctime)))
			else:
				break

			MyVarBackUpListFTP = self.FTP.nlst()

			while len(MyVarBackUpListFTP) > self.Data['MaxFile']['FTP']+1:
				del MyVarBackUpListFTP[0]
				self.FTP.delete(min(MyVarBackUpListFTP))

			
		self.ClassSys.AddReading(self.Device, 'FilesFHEM', str(len(os.listdir(self.Data['Dir']['FHEM']))))
		self.ClassSys.AddReading(self.Device, 'FilesFTP', str(len(self.FTP.nlst())-1))

		self.ClassSys.AddReading(self.Device, 'state', 'Finish')
		self.ClassSys.AddReading(self.Device, 'LastRun', self.DateTime)


##############################################################
### Program

MyVarRun = MyBack2FTPClass(MyVarSysData)
MyVarRun.ClassSys.ExecuteReadings()

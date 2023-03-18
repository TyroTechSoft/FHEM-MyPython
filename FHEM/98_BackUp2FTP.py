#!/usr/bin/env python3

#######################################################################################################################################
#                          
#  FHEM-MyPython                                                                                                    
#   98_BackUp2FTP.py - V0.1.8
#    Date: 18.03.2023 - 10:24 Uhr
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

	MyVarSysData['VersionInfo'] = {
		'Version': "V0.1.8",
		'Date': "18.03.2023 - 10:24 Uhr"}

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
### Size Calculator Function

def MyFunctionSizeCalculator(MyVarValue):
	MyVarB = float(MyVarValue)
	MyVarKB = float(1024)
	MyVarMB = float(MyVarKB ** 2)
	MyVarGB = float(MyVarKB ** 3)
	MyVarTB = float(MyVarKB ** 4)

	if MyVarB < MyVarKB:
		return '{0} {1}'.format(MyVarB,'Bytes' if 0 == MyVarB > 1 else 'Byte')
	elif MyVarKB <= MyVarB < MyVarMB:
		return '{0:.2f} KB'.format(MyVarB / MyVarKB)
	elif MyVarMB <= MyVarB < MyVarGB:
		return '{0:.2f} MB'.format(MyVarB / MyVarMB)
	elif MyVarGB <= MyVarB < MyVarTB:
		return '{0:.2f} GB'.format(MyVarB / MyVarGB)
	elif MyVarTB <= MyVarB:
		return '{0:.2f} TB'.format(MyVarB / MyVarTB)


##############################################################
### Back2FTP Class

class MyBackUp2FTPClass:
	def __init__(self, MyVarSysData):
		self.ClassSys = MyClassSys(MyVarSysData)
		self.DateTime = str(datetime.now().strftime("%d.%m.%Y %H:%M"))
		self.Device = MyVarSysData['Device']
		self.FTP_TLS = False
		self.FTP_Resp = "NONE"
		MyVarDeviceData = self.ClassSys.FHEM.get(name=self.Device)

		self.ClassSys.SetReading(self.Device, 'state', 'Running')
		self.ClassSys.SetReading(self.Device, 'Version', MyVarSysData['VersionInfo']['Version'])
		self.ClassSys.SetReading(self.Device, 'VersionDate', MyVarSysData['VersionInfo']['Date'])

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
			print("BackUp2FTP: FHEM Error: Cannot find or access FHEM Dir!")
			exit()


########### FTP Connect

		try:
			try:
				self.FTP = FTP_TLS(timeout=10)
				self.FTP.connect(self.Data['IP'])
				self.FTP.login(user=self.Data['User'], passwd=self.Data['Pass'])
				self.FTP.prot_p() 
#				self.FTP.retrlines('LIST')
				self.ClassSys.AddReading(self.Device, 'FTP-Protocol', 'FTP_TSL')
			except:
				self.FTP = FTP(host= self.Data['IP'], user= self.Data['User'], passwd= self.Data['Pass'])
				self.ClassSys.AddReading(self.Device, 'FTP-Protocol', 'FTP')

			self.FTP.encoding = "utf-8"
			self.FTP.cwd(self.Data['Dir']['FTP'])
		except:
			self.ClassSys.SetReading(self.Device, 'state', 'FTP Error: Cannot connect!')
			print("BackUp2FTP: FTP Error: Cannot connect!")
			exit()


########### Upload File

		try:
			MyVarFile = max(glob.iglob(self.Data['Dir']['FHEM'] + '/*'), key=os.path.getctime)
			MyVarFileName = ntpath.basename(MyVarFile)
			self.ClassSys.SetReading(self.Device, 'FileName', MyVarFileName)
			self.ClassSys.SetReading(self.Device, 'FileSize', MyFunctionSizeCalculator(os.path.getsize(MyVarFileName)))

			try:
				with open(MyVarFileName, 'rb') as MyVarUpload:
					self.FTP.storbinary(f'STOR {MyVarFileName}', MyVarUpload)
				self.ClassSys.AddReading(self.Device, 'FTP-Mode', 'Binary')
			except:
				with open(MyVarFileName, 'rb') as MyVarUpload:
					self.FTP.storlines(f'STOR {MyVarFileName}', MyVarUpload)
				self.ClassSys.AddReading(self.Device, 'FTP-Mode', 'ASCII')

		except:
			self.ClassSys.SetReading(self.Device, 'state', 'FTP Error: Cannot Upload File!')
			print("BackUp2FTP: FTP Error: Cannot Upload File!")
			exit()


########### Delete old Files

		while True:
			MyVarBackUpListFHEM = os.listdir(self.Data['Dir']['FHEM'])

			if len(MyVarBackUpListFHEM) > self.Data['MaxFile']['FHEM']:
				os.remove(os.path.abspath(self.Data['Dir']['FHEM'] + "/" + min(MyVarBackUpListFHEM, key= os.path.getctime)))
			else:
				break

			MyVarBackUpListFTP = self.FTP.nlst()

			try:
				MyVarBackUpListFTP.remove("..")
			except:
				pass

			try:
				MyVarBackUpListFTP.remove(".")
			except:
				pass

			while len(MyVarBackUpListFTP) > self.Data['MaxFile']['FTP']:
				MyVarDelFileFTP = min(MyVarBackUpListFTP)
				MyVarBackUpListFTP.remove(MyVarDelFileFTP)
				self.FTP.delete(MyVarDelFileFTP)

			
		self.ClassSys.AddReading(self.Device, 'FilesFHEM', str(len(os.listdir(self.Data['Dir']['FHEM']))))
		self.ClassSys.AddReading(self.Device, 'FilesFTP', str(len(self.FTP.nlst())-1))

		self.ClassSys.AddReading(self.Device, 'state', 'Finish')
		self.ClassSys.AddReading(self.Device, 'LastRun', self.DateTime)
		print("BackUp2FTP: BackUp wurde hochgelade!")


########### Clode Connection

		self.FTP.quit()


##############################################################
### Program

MyVarRun = MyBackUp2FTPClass(MyVarSysData)
MyVarRun.ClassSys.ExecuteReadings()
# -*- coding: utf-8 -*- 
import os
import sys
import ftplib

class FTPHandler:
	ftp = ftplib.FTP()
	def __init__(self,host,port=21):
		print("FTP host:port, {}:{}".format(host, port))
		self.ftp.connect(host,port)

	def login(self,user,passwd):
		self.ftp.login(user,passwd)

	def download_file(self,local_file,remote_file):
		file_handler = open(local_file,'wb')
		self.ftp.retrbinary('RETR '+remote_file,file_handler.write)
		file_handler.close()
		print("Get file from FTP Done: "+remote_file+" >>> "+local_file)
		return True

	def close(self):
		self.ftp.quit()
		print("ftp close")

	#def __del__(self):
	#	self.ftp.quit()
	#	print("ftp close with FTPHandler deconstruct")

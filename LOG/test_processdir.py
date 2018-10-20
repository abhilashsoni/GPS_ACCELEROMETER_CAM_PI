import sys
import os
# from gps import *
import time
# import IMU
# import zlib, base64
# import firebase_admin
# from firebase_admin import credentials,firestore
import threading
# from picamera import PiCamera
import urllib2
from threading import Thread, Event
import requests
import errno
from socket import error as SocketError
import difflib
# import pigpio
# import serial
rx=26

polfile = ''
arduinofile = ''
gpsfile = ''
imagefile = ''



gpsfile_limit = 3000
polfile_limit = 3000
arduinofile_limit = 10
imagefile_limit = 500



gpsfile_lines = gpsfile_limit 
polfile_lines = polfile_limit
arduinofile_lines = arduinofile_limit
imagefile_lines = imagefile_limit

address_prefix =''          #'/home/pi/Documents/LOG/'

def process_directory(localdir):
	flist = os.listdir(localdir)
	print ("No of files in {} = {}".format(localdir,len(flist)))
	if (len(flist)>2):
		for localfile in flist[1:-1]:				#0th file in .keep , last file is currently in use
			print ("Processing file {}".format(localfile))
			f = open(localdir+'/'+localfile,'r')
			print ("Opened file {}".format(localfile))
			lines=f.readlines()
			f.close()
			print ( "Read {} lines in {}".format(len(lines),localdir))
			dic = {}
			# if (len(lines)>data_lines_uploaded):
			for line in lines:
				ltime = line.split(',')[0]
				dic[unicode(ltime,'utf-8')] = unicode(line,'utf-8')
			print ("######################Dictionary made!")
			print ( str(dic))
			# doc_ref = db.collection(u'sensor_data_mp').document(localdir)
			# doc_ref.update(dic)    
			print( "#####################Updated to firebase")    
			
			os.unlink(localdir+'/'+localfile)

def write_to_firebase():
	global address_prefix
	retry_on = (requests.exceptions.Timeout,requests.exceptions.ConnectionError,requests.exceptions.HTTPError,IOError)
	time_out=2
	# print ("Started process write to firebase")
	while True:
		if (not internet_on()):
			time.sleep(time_out)
			continue
		try:
			print("Trying to update to firebase")
			# process_directory(u'gps')
			# process_directory(u'image')
			# process_directory(u'poldata')
			process_directory(u'arduino')
		except IOError ,e :
			print("Error opening file: {}".format(str(e)))
		except retry_on:
			pass
		finally:
			time.sleep(time_out)

def internet_on():
	exc = (urllib2.URLError, urllib2.HTTPError)
	try:
		urllib2.urlopen('http://216.58.192.142',timeout=3)
		print("Internet connection present")
		return True
	except exc:		
		print("Internet connection not present")	
		return False
	except socket.timeout:
		print("Internet connection not present")
		return False
	except SocketError as e:
		if e.errno !=errno.ECONNRESET:
		    #print(3)
		    raise
		pass

# cred = credentials.Certificate("serviceAccountKey.json")
# firebase_admin.initialize_app(cred)

# db = firestore.client()
# # gps_file_ref = db.collection(u'sensor_data_mp').document(u'gps')
# arduino_file_ref = db.collection(u'sensor_data_mp').document(u'arduino')
# # poldata_file_ref = db.collection(u'sensor_data_mp').document(u'poldata')
# # image_file_ref = db.collection(u'sensor_data_mp').document(u'image')
# # gps_file_ref.set({})
# arduino_file_ref.set({})
# # poldata_file_ref.set({})
# # image_file_ref.set({})
# os.system('clear')


write_to_firebase()
# f.close()
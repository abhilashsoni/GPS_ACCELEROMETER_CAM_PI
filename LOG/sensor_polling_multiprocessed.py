import sys
import os
from gps import *
import time
# import threading
import IMU
import zlib, base64
import firebase_admin
from firebase_admin import credentials,firestore
from picamera import PiCamera
import urllib
# from threading import Thread, Event
import multiprocessing as mp
import requests
import errno
from socket import error as SocketError
import difflib
import pigpio
import serial
rx=26

address_prefix =''          #'/home/pi/Documents/LOG/'
accfile_lines_uploaded = 0
poldata_lines_uploaded = 0
data_lines_uploaded = 0


try:
    import struct
except ImportError:
    import ustruct as struct
    
pi=pigpio.pi()
if not pi.connected:
    exit(0)
    
pi.set_mode(rx,pigpio.INPUT)
pi.bb_serial_read_open(rx,9600,8)
buffer=[]
 
stop_event = Event()
#when internet is not connected it will retry sending data
def write_to_firebase(db):
		global address_prefix
        retry_on = (requests.exceptions.Timeout,requests.exceptions.ConnectionError,requests.exceptions.HTTPError,IOError)
        time_out=3
        while True:
        		if(!internet_on()):
        			time.sleep(time_out)
        			continue
                try:
                		#upload new values from data file
                        f = open(address_prefix+'data.txt','r')
                        lines=f.readlines()
                        if (len(lines)>data_lines_uploaded):
                        	for i in range(data_lines_uploaded,len(lines)):
                        		doc_ref = db.collection(u'sensor_data_2').document(u'LOG')
                        		ltime = lines[i].split(',')[0]
		                        doc_ref.update({unicode(ltime,'utf-8') :unicode(lines[i],'utf-8')})
		                        data_lines_uploaded += 1
		                f.close()
		                #upload new values from accel file
                        f = open(address_prefix+'accel.txt','r')
                        lines=f.readlines()
                        if (len(lines)>accfile_lines_uploaded):
                        	for i in range(accfile_lines_uploaded,len(lines)):
                        		doc_ref = db.collection(u'sensor_data_2').document(u'AccFile')
                        		ltime = lines[i].split(',')[0]
		                        doc_ref.update({unicode(ltime,'utf-8') :unicode(lines[i],'utf-8')})
		                        accfile_lines_uploaded += 1
		                f.close()
		                #upload new values from Pol_data file
                        f = open(address_prefix+'Pol_data.txt','r')
                        lines=f.readlines()
                        if (len(lines)>poldata_lines_uploaded):
                        	for i in range(poldata_lines_uploaded,len(lines)):
                        		doc_ref = db.collection(u'sensor_data_2').document(u'Pol_data')
                        		ltime = lines[i].split(',')[0]
		                        doc_ref.update({unicode(ltime,'utf-8') :unicode(lines[i],'utf-8')})
		                        poldata_lines_uploaded += 1
		                f.close()
		                time.sleep(time_out)
                except retry_on:
                        time.sleep(time_out)
                        continue
                else:
                        break

#checks it internet connection is available
def internet_on():
	exc = (urllib.URLError, urllib.HTTPError)
	try:
		urllib.urlopen('http://216.58.192.142',timeout=3)
		return True
	except exc:			
                return False
	except socket.timeout:
		return False
	except SocketError as e:
            if e.errno !=errno.ECONNRESET:
                #print(3)
                raise
            pass

# thread to take accelerometer readings and writing it in a file and firebase
def accel():
    global address_prefix
    while True:
        #print(count)
        # print(1)
        local = time.asctime(time.localtime(time.time()))
        string = address_prefix+'accel.txt'
        #acc='/accel/acc%s'%local
        fa=open(string,"a+")
	#collecting the value of accelerometer every .5 sec So 60 values in 30sec
        ACCx=IMU.readACCx()
        ACCy=IMU.readACCy()
        ACCz=IMU.readACCz()
        x=((ACCx*0.244)/100)
        y=((ACCy*0.244)/100)
        z=((ACCz*0.244)/100)
        print(("X = %f\t"%x),)
        print(("Y = %f\t"%y),c)
        print(("Z = %f\t"%z))    
        #ts=time.asctime(time.localtime(time.time()))
        coordinates = "X = %f\tY = %f\tZ=%f"%(x,y,z)
        time_str = str(local)
        s=("%s\t,\t%s\n"%(time_str,coordinates)) 
        fa.write(s)
        fa.close()
        # time.sleep(0.5)
        # print('Checking Internet')
        # #writing data to file and sending it on firebase
        # result=internet_on()
        # if result:
        #    print('Internet is on')
        #    if os.path.exists(address_prefix+"dataofaccel.txt"):
        #            print('It exists')
        #            f_noc=open(address_prefix+"dataofaccel.txt","a+")
        #            f_noc.seek(0,0)
        #            lines=f_noc.readlines()
        #            if lines!='':
        #                    for x in lines:
        #                        action_thread=Thread(target=do_actions,args=(u'AccFile',x,))
        #                        action_thread.start()
                                
        #                    os.remove(address_prefix+"dataofaccel.txt")
           
        #    # s=("%s\t\t%s\n"%(coordinates,time_str)) 
        #    action_thread_4 = Thread(target=do_actions,args=(u'AccFile',s,))
        #    action_thread_4.start()       
        # else:
        #    print('Internet is not there')
        #    f_noc=open(address_prefix+"dataofaccel.txt","a+")   
        #    f_noc.write(s)
        #    f_noc.close()
        #    # time.sleep(0.5)
        time.sleep(0.5)  
def writeLog(logfile):
    global address_prefix
    while True:
      
      # print(1)
      global buffer
      flag = 0  
      localtime = time.asctime(time.localtime(time.time()))
      print(('latitude    ' , gpsd.fix.latitude))
      print(('longitude   ' , gpsd.fix.longitude))
      print(('Time        ' , localtime))
      string1 = (address_prefix+'images/img%s.jpg')%(localtime)
      camera=PiCamera()
      camera.capture(string1)
      camera.close()
      # time.sleep(0.5)
      print(string1)
      imag=string1
	  #encoding jpeg to text and compressing the text
      with open(imag,"rb") as imageFile:
       image_64= base64.b64encode(zlib.compress(bytes(imag,'utf-8'),9))
      
      avpg=0
      while avpg==0:
            #time.sleep(1.5)
            (count,data1)=pi.bb_serial_read(rx)
            buffer += data1
            #print(buffer)
            #print(1)
            while buffer and buffer[0] != 0x42:
                buffer.pop(0)
            #print(2)
            if len(buffer) > 200:
                buffer = []  # avoid an overrun if all bad data
                continue
            #print(3)
            if len(buffer)<33:
                continue
            #print(4)
            if buffer[1] != 0x4d:
                buffer.pop(0)
                continue
            #print(5)
            frame_len = struct.unpack(">H", bytes(buffer[2:4]))[0]
            if frame_len != 28:
                buffer = []
                continue
            
            #if len(buffer)<33:
             #   continue
     
            frame = struct.unpack(">HHHHHHHHHHHHHH", bytes(buffer[4:32]))
     
            pm10_standard, pm25_standard, pm100_standard, pm10_env, \
                pm25_env, pm100_env, particles_03um, particles_05um, particles_10um, \
                particles_25um, particles_50um, particles_100um, skip, checksum = frame
     
            check = sum(buffer[0:30])
     
            if check != checksum:
                buffer = []
                continue
     
            print("Concentration Units (standard)")
            print("---------------------------------------")
            print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" %
                  (pm10_standard, pm25_standard, pm100_standard))
            print("Concentration Units (environmental)")
            print("---------------------------------------")
            print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" % (pm10_env, pm25_env, pm100_env))
            print("---------------------------------------")
            print("Particles > 0.3um / 0.1L air:", particles_03um)
            print("Particles > 0.5um / 0.1L air:", particles_05um)
            print("Particles > 1.0um / 0.1L air:", particles_10um)
            print("Particles > 2.5um / 0.1L air:", particles_25um)
            print("Particles > 5.0um / 0.1L air:", particles_50um)
            print("Particles > 10 um / 0.1L air:", particles_100um)
            print("---------------------------------------")
            gf=open(address_prefix+"Pol_data.txt","a+")
            ltime=time.asctime(time.localtime(time.time()))
        #f.write("Time: %s\tPM 1.0: %d\tPM2.5: %d\tPM10: %d" %str(ltime) %pm10_standard %pm25_standard %pm100_standard)
            s=("PM 1.0: %d\tPM2.5: %d\tPM10: %d" %(pm10_standard, pm25_standard, pm100_standard))
            pol_data=str(ltime)+','+s+'\n'
            # gf.write("Time:%s " %str(ltime))
            # gf.write("PM1.0:%d " %pm10_standard)
            # gf.write("PM2.5:%d " %pm25_standard)
            # gf.write("PM10:%d " %pm100_standard)
            gf.write(pol_data)
            gf.close()
            
            #fb1.post('Pol_data',data)
            buffer = buffer[32:]
            avpg=1
      data="%s\t,Lat:%f\tLong:%f\tImage:%s\tImgAsTxt:%s" %(localtime,gpsd.fix.latitude,gpsd.fix.longitude,string1,image_64) 
      f=open(logfile,"a+")
      f.write("%s\n" %data)  
      f.close()   
      # result=internet_on()
      # if result:
      #      print('Internet is there')
      #      if os.path.exists(address_prefix+"data.txt"):
      #              print('It exists')
      #              f_noc_p=open(address_prefix+"data.txt","a+")
      #              f_noc_p.seek(0,0)
      #              lines=f_noc_p.readlines()
      #              if lines!='':
      #                      for x in lines:
      #                              if flag==0:
      #                                  action_thread_10 = Thread(target=do_actions,args=(u'LOG',x,))
      #                                  action_thread_10.start()
      #                                  flag=1
      #                              else:
      #                                   action_thread_11=Thread(target=do_actions,args=(u'Pol_data',x,))
      #                                   action_thread_11.start()
      #                                   flag=0
      #                      os.remove(address_prefix+"data.txt")
           
      #      action_thread_12 = Thread(target=do_actions,args=('LOG',data,))
      #      action_thread_12.start()
      #      action_thread_13 = Thread(target=do_actions,args=('Pol_data',pol_data,))
      #      action_thread_13.start()
          
      # else:
      #      print('Internet is not there:')
      #      f_noc_p=open(address_prefix+"data.txt","a+")   
      #      datafile_1='%s\n%s\n'%(data,pol_data)
      #      f_noc_p.write("%s"%datafile_1)
      #      f_noc_p.close()
      #      # time.sleep(2)
    time.sleep(10)
    
#Beginning of the program
IMU.detectIMU()
IMU.initIMU()
gpsd = None

logfile=address_prefix+"LOG.txt"
#Your database name in firebase
# firebase=firebase.FirebaseApplication('https://sensor-with-avpg.firebaseio.com/', None)
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
log_ref = db.collection(u'sensor_data_2').document(u'LOG')
acc_file_ref = db.collection(u'sensor_data_2').document(u'AccFile')
poldata_file_ref = db.collection(u'sensor_data_2').document(u'Pol_data')
log_ref.set({u'0' : u"Collected Data below"})
acc_file_ref.set({u'0' : u"Collected Data below"})
poldata_file_ref.set({u'0' : u"Collected Data below"})
os.system('clear')

class GpsPoller():
  def __init__(self):
    # threading.Thread.__init__(self)
    global gpsd
    gpsd = gps(mode=WATCH_ENABLE) 
    self.current_value = None
    self.running = True
  def poll_gps(self):
  	global gpsd
    while gpsp.running:
      next(gpsd) 
  def run(self):
    p = mp.Process(target=self.poll_gps)
    p.start()
if __name__ == '__main__':

  gpsp = GpsPoller() 
  gpsp.run()

  writelog_p = mp.Process(target=writeLog,args=(logfile,))
  writelog_p.start()
  accel_p = mp.Process(target=accel)
  accel_p.start()

  write_to_firebase(db)

# action_thread_1=Thread(target=accel,args=())
# action_thread_1.start()

# writeLog(logfile)
# f.close()

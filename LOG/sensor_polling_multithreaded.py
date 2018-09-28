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
from threading import Thread, Event
import requests
import errno
from socket import error as SocketError
import difflib
import pigpio
import serial
rx=26

polfile = ''
accelfile = ''
gpsfile = ''
imagefile = ''



gpsfile_limit = 3000
polfile_limit = 3000
accelfile_limit = 3000
imagefile_limit = 500



gpsfile_lines = gpsfile_limit 
polfile_lines = polfile_limit
accelfile_lines = accelfile_limit
imagefile_lines = imagefile_limit

address_prefix =''          #'/home/pi/Documents/LOG/'


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

def process_directory(localdir):
  flist = os.listdir(localdir)
  if (len(flist)>2):
    for localfile in flist[1:-1]:
      f = open(localfile,'r')
      lines=f.readlines()
      dic = {}
      # if (len(lines)>data_lines_uploaded):
      for line in lines:
        ltime = line.split(',')[0]
        dic[unicode(ltime,'utf-8')] = unicode(line,'utf-8')
      doc_ref = db.collection(u'sensor_data_mp').document(localdir)
      doc_ref.update(dic)        
      f.close()
      os.unlink(localdir+'/'+localfile)
def write_to_firebase(db):
    global address_prefix
    retry_on = (requests.exceptions.Timeout,requests.exceptions.ConnectionError,requests.exceptions.HTTPError,IOError)
    time_out=10
    while True:
      if(!internet_on()):
        time.sleep(time_out)
        continue
      try:
        process_directory(u'gps')
        process_directory(u'image')
        process_directory(u'poldata')
        process_directory(u'accel')
      except retry_on:
        pass
      finally:
        time.sleep(time_out)
          

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
def writeaccel():
    global address_prefix,accelfile,accfile_lines_uploaded,accelfile_limit
    while True:
      if ( accelfile_lines >= accfile_limit):
        ltime=str(time.asctime(time.localtime(time.time())))
        accelfile = 'accel/'+ltime+ 'accel.txt'
        accelfile_lines = 0
      #print(count)
      # print(1)
      local = time.asctime(time.localtime(time.time()))
      # string = address_prefix+'accel.txt'
      #acc='/accel/acc%s'%local
      fa=open(address_prefix+accelfile,"a+")
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
      time.sleep(0.5)
def writegps():
    global address_prefix,gpsfile,gpsfile_limit,gpsfile_lines
    while True:
      if ( gpsfile_lines >= gpsfile_limit):
          ltime=str(time.asctime(time.localtime(time.time())))
          gpsfile = 'gps/'+ltime+ 'gps.txt'
          gpsfile_lines = 0
      # print(1)
      localtime = time.asctime(time.localtime(time.time()))
      print(('latitude    ' , gpsd.fix.latitude))
      print(('longitude   ' , gpsd.fix.longitude))
      print(('Time        ' , localtime))
      
      data="%s\t,Lat:%f\tLong:%f" %(localtime,gpsd.fix.latitude,gpsd.fix.longitude) 
      f=open(address_prefix+gpsfile,"a+")
      f.write("%s\n" %data)  
      f.close()   
      
    time.sleep(10)  
def writeimage():
    global address_prefix,imagefile,imagefile_lines,imagefile_limit
    while True:
      if ( imagefile_lines >= imagefile_limit):
          ltime=str(time.asctime(time.localtime(time.time())))
          imagefile = 'image/'+ltime+ 'image.txt'
          imagefile_lines = 0
      # print(1)
      global buffer
      localtime = time.asctime(time.localtime(time.time()))
      # print(('Time        ' , localtime))
      string1 = address_prefix+'image/img.jpg'
      camera=PiCamera()
      camera.capture(string1)
      camera.close()
      # time.sleep(0.5)
      # print(string1)
      imag=string1
    #encoding jpeg to text and compressing the text
      with open(imag,"rb") as imageFile:
       image_64= base64.b64encode(zlib.compress(bytes(imag,'utf-8'),9))
      #delete image file
      data="%s,ImgAsTxt:%s" %(localtime,image_64) 
      f=open(imagefile,"a+")
      f.write("%s\n" %data)  
      f.close()   
      os.unlink(string1)
    time.sleep(10)
def writepol():
    global address_prefix
    while True:
      if ( polfile_lines >= polfile_limit):
          ltime=str(time.asctime(time.localtime(time.time())))
          polfile = 'pol/'+ltime+ 'pol.txt'
          polfile_lines = 0
      # print(1)
      global buffer
      
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
        gf=open(address_prefix+polfile,"a+")
        ltime=time.asctime(time.localtime(time.time()))
    #f.write("Time: %s\tPM 1.0: %d\tPM2.5: %d\tPM10: %d" %str(ltime) %pm10_standard %pm25_standard %pm100_standard)
        s=("PM 1.0: %d\tPM2.5: %d\tPM10: %d" %(pm10_standard, pm25_standard, pm100_standard))
        pol_data=str(ltime)+','+s+'\n'
        gf.write(pol_data)
        gf.close()
        
        #fb1.post('Pol_data',data)
        buffer = buffer[32:]
        avpg=1
        time.sleep(1)
    
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
gps_file_ref = db.collection(u'sensor_data_mp').document(u'gps')
accel_file_ref = db.collection(u'sensor_data_mp').document(u'accel')
poldata_file_ref = db.collection(u'sensor_data_mp').document(u'poldata')
image_file_ref = db.collection(u'sensor_data_mp').document(u'image')
log_ref.set({})
acc_file_ref.set({})
poldata_file_ref.set({})
image_file_ref.set({})
os.system('clear')

class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd
    gpsd = gps(mode=WATCH_ENABLE) 
    self.current_value = None
    self.running = True
 
  def run(self):
    global gpsd
    while gpsp.running:
      next(gpsd) 
if __name__ == '__main__':
  gpsp = GpsPoller() 
  gpsp.start()
count=0

accel_thread=Thread(target=writeaccel)
accel_thread.start()
gps_thread=Thread(target=writegps)
gps_thread.start()
image_thread=Thread(target=writeimage)
image_thread.start()
pol_thread=Thread(target=writepol)
pol_thread.start()



write_to_firebase(db)
# f.close()

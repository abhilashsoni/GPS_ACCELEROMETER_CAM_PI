import sys
import os
# from gps import *
import time
import firebase_admin
from firebase_admin import credentials,firestore
import re
from datetime import datetime


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
log_ref = db.collection(u'sensor_data_latency').document(u'LOG')
acc_file_ref = db.collection(u'sensor_data_latency').document(u'AccFile')
log_ref.set({u'0' : u"Collected Data below"})
acc_file_ref.set({u'0' : u"Collected Data below"})

dt = u'sgsgsgsgs'

cnt = 0
sumtotal = 0
sum_square = 0

while (cnt<100):
	ltime = time.asctime(time.localtime(time.time()))
	log_ref.update({unicode(ltime,'utf-8') :dt})
	acc_file_ref.update({unicode(ltime,'utf-8') :dt})
	ftime = time.asctime(time.localtime(time.time()))
	print(ltime)
	print(ftime)
	start_time = datetime.strptime(ltime, "%a %b %d %H:%M:%S %Y")
	finish_time = datetime.strptime(ftime, "%a %b %d %H:%M:%S %Y")
	dif = finish_time - start_time
	measure = dif.total_seconds()
	sumtotal = sumtotal + measure
	sum_square = sum_square + measure*measure
	print('Wrote to database')
	cnt = cnt+1;

expectation = (float(sumtotal)/100)
expectation_sq = float(sum_square)/100
print(expectation)
print(expectation_sq-expectation*expectation)

# print("localtime : {}".format(ltime))
#time.sleep(0.5)

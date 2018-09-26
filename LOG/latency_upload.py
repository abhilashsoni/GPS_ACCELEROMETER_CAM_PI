import sys
import os
# from gps import *
import time
import firebase_admin
from firebase_admin import credentials,firestore
import re
from datetime import datetime
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('Agg')


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
log_ref = db.collection(u'sensor_data_latency').document(u'LOG')
acc_file_ref = db.collection(u'sensor_data_latency').document(u'AccFile')
log_ref.set({u'0' : u"Collected Data below"})
acc_file_ref.set({u'0' : u"Collected Data below"})

dt = u'sgsgsgsgs'
X_list = range(95,200,5)
Y_list = []
for i in range(95,200,5):
	cnt = 0
	sumtotal = 0
	sum_square = 0
	dic = {}
	for j in range(i):
		ltime = unicode(time.asctime(time.localtime(time.time())),'utf-8')
		dic [ltime] = dt
	while (cnt<50):
		try:
			ltime = time.asctime(time.localtime(time.time()))
			log_ref.update(dic)
			# acc_file_ref.update({unicode(ltime,'utf-8') :dt})
			ftime = time.asctime(time.localtime(time.time()))
			# print(ltime)
			# print(ftime)
			start_time = datetime.strptime(ltime, "%a %b %d %H:%M:%S %Y")
			finish_time = datetime.strptime(ftime, "%a %b %d %H:%M:%S %Y")
			dif = finish_time - start_time
			measure = dif.total_seconds()
			sumtotal = sumtotal + measure
			sum_square = sum_square + measure*measure
			# print('Wrote to database')
		except:
			pass
		finally:
		cnt = cnt+1;

	expectation = (float(sumtotal)/(50*i))
	expectation_sq = float(sum_square)/(50*i*i)
	print("Packet Size : {} Average: {}+- {}".format(i,expectation,sqrt(expectation_sq-expectation*expectation)))
	Y_list.append(expectation)
	# print(sqrt(expectation_sq-expectation*expectation))
print( Y_list )	
plt.plot(X_list,Y_list)
plt.show()

# print("localtime : {}".format(ltime))
#time.sleep(0.5)

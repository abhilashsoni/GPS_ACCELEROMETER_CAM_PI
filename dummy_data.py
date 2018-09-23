import sys
import os
# from gps import *
import time
import firebase_admin
from firebase_admin import credentials,firestore


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
log_ref = db.collection(u'sensor_data').document(u'LOG')
acc_file_ref = db.collection(u'sensor_data').document(u'AccFile')
log_ref.set({u'0' : u"Collected Data below"})
acc_file_ref.set({u'0' : u"Collected Data below"})



while (True):
	ltime = time.asctime(time.localtime(time.time()))
	dt = u'sgsgsgsgs'
	log_ref.update({unicode(ltime,'utf-8') :dt})
	acc_file_ref.update({unicode(ltime,'utf-8') :dt})
	print('Wrote to database')
	# print("localtime : {}".format(ltime))
	time.sleep(0.5)
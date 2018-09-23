import firebase_admin
from firebase_admin import credentials, firestore
import re
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
doc_ref = db.collection(u'sensor_data').document(u'LOG')

#try:
doc = doc_ref.get()
a = doc.to_dict()
# print(a)
keys = a.keys()
#print(keys)
keys = sorted(a.iterkeys())
#print('************')
#print(keys)
#print(keys[0])
#print(keys[1])
#print(keys[2])
t = datetime.strptime(keys[1], "%a %b %d %H:%M:%S %Y")
#print(t)

del keys[0]
del keys[0]
sum = 0
sum_square = 0
for key in keys:
	#print(key)
	# Sun Sep 23 19:57:44 2018
	keyparsed = datetime.strptime(key, "%a %b %d %H:%M:%S %Y")
	#print(keyparsed)
	dif = keyparsed-t
	t = keyparsed
	#print(dif)
	#k = dif.split(':')
	#measure = k[0]*3600+k[1]*60+k[2]
	measure = dif.total_seconds()
	print(measure)
	sum = sum + measure
	sum_square = sum_square+measure*measure
expectation = (float(sum)/(len(keys)))
expectation_sq = float(sum_square)/len(keys)
print(expectation)
print(expectation_sq-expectation*expectation)
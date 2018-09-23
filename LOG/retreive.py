import firebase_admin
from firebase_admin import credentials, firestore
import re

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
doc_ref = db.collection(u'sensor_data').document(u'LOG')

#try:
doc = doc_ref.get()
a = doc.to_dict()
# print(a)
keys = a.keys()
key = keys[0]
k = map(int, re.findall(r'\d+', key))
t = k[2]*60+k[3]
del keys[0]
sum = 0
for key in keys:
	if(key!=0):
		k = map(int, re.findall(r'\d+', key))
		if(len(k)>1):
			dif = t - k[2]*60+k[3]
			t = k[2]*60+k[3]
			sum = sum + dif

print(sum/len(keys))



#except google.cloud.exceptions.NotFound:
#    print('No such document!')


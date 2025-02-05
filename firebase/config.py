import pyrebase

fireBaseConfig = {
    "apiKey": "AIzaSyBSwpJF8Zyr3UevjIsy_hNFU-jMYq--Beg",
    "authDomain": "eduvelo-v1.firebaseapp.com",
    "databaseURL": "https://eduvelo-v1-default-rtdb.firebaseio.com",
    "projectId": "eduvelo-v1",
    "storageBucket": "eduvelo-v1.firebasestorage.app",
    "messagingSenderId": "520880508199",
    "appId": "1:520880508199:web:112b491017a9805c386d02",
    "measurementId": "G-8HZVKHNDQW"
}

firebase = pyrebase.initialize_app(fireBaseConfig)

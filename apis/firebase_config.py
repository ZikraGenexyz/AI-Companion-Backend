import pyrebase

firebaseConfig = {
  "apiKey": os.getenv('FIREBASE_API_KEY'),
  "authDomain": "companion-app-1b431.firebaseapp.com",
  "projectId": "companion-app-1b431",
  "storageBucket": "companion-app-1b431.firebasestorage.app",
  "messagingSenderId": "484116816802",
  "appId": "1:484116816802:web:ab65953efc39e67fd888fb",
  "measurementId": "G-N7CJ13Q3ND"
};

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()
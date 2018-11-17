import os
import pyrebase
from linebot import (LineBotApi, WebhookHandler)

namaBot = "rion"
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('SECRET_TOKEN'))
google_key = os.environ.get('GOOGLE_API_KEY')

config = {
    "apiKey": os.environ.get('FIREBASE_API_KEY'),
    "authDomain": os.environ.get('FIREBASE_AUTH_DOMAIN'),
    "databaseURL": os.environ.get('FIREBASE_LINK_DATABASE'),
    "storageBucket": os.environ.get('FIREBASE_STORAGE_BUCKET')
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

notifikasi = False
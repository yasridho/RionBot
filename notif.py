import sesuatu
import os
import schedule
import time

from datetime import datetime
from threading import Timer
from acc import (namaBot, google_key, line_bot_api, handler, db, notifikasi)
from linebot.models import *

Jalankan = False



def yee():
	line_bot_api.push_message('U3fed832cbef28b87b7827b306506c8d5', TextSendMessage(text="Yeeee"))



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	text = event.message.text
	sender = event.source.user_id

	if text == "Run notif":
		Jalankan = True
		line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Notif berjalan"))
		x = datetime.today()
		y = x.replace(second=x.second+10)
		delta_t = y - x
		secs = delta_t.seconds+1
		t = Timer(secs, yee)
		t.start()
		
	elif text == "Stop notif":
		Jalankan = False
		line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Notif berhenti"))
		t.stop()
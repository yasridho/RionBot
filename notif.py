import sesuatu
import os
import schedule

from acc import (namaBot, google_key, line_bot_api, handler, db)
from linebot.models import *

def notifikasi():
	line_bot_api.push_message('U3fed832cbef28b87b7827b306506c8d5', TextSendMessage(text="Yeeee"))

schedule.every().day.at("17:13").do(notifikasi)

while True:
	schedule.run_pending()
	time.sleep(1)
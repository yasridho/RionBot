import errno
import os
import sys, random, datetime, time, re

from datetime import datetime
from acc import (line_bot_api, namaBot, owner, handler)
from sesuatu import search_movie_imdb
from linebot.models import *


perintah = {}

@handler.add(PostbackEvent)
def handle_postback(event):
	if isinstance(event.source, SourceGroup):
		kirim = event.source.sender_id
	elif isinstance(event.source, SourceRoom):
		kirim = event.source.room_id
	else:
		kirim = event.source.user_id
	
	try:

		if event.postback.data[0] == '/':
			data = event.postback.data[1:].split(" ",1)
			if len(data) > 1:
				cmd, args = data[0].lower(), data[1]
			else:
				cmd, args = data[0].lower(), ""

	except Exception as e:
		try:
			et, ev, tb = sys.exc_info()
			lineno = tb.tb_lineno
			fn = tb.tb_frame.f_code.co_filename
			if sender != owner:
				line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Oopps.. '+namaBot.capitalize()+' ada kesalahan kak :('),TextSendMessage(text='Tapi tenang kak, laporan kesalahan ini terkirim ke owner untuk diperbaiki ;D')])
			line_bot_api.push_message(owner, TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e))))
		except:
			line_bot_api.push_message(owner, TextSendMessage(text="Undescribeable error detected!!"))
					

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
	if isinstance(event.source, SourceGroup):
		kirim = event.source.sender_id
	elif isinstance(event.source, SourceRoom):
		kirim = event.source.room_id
	else:
		kirim = event.source.user_id

	sender = event.source.user_id
	try:

		if sender in perintah:
			komando, waktu = perintah[sender]

			if komando == 'Cari film imdb':
				hasil = search_movie_imdb(text)
				pesan = FlexSendMessage(
					alt_text='Hasil pencarian: '+text,
					contents=CarouselContainer(
						contents=hasil[:10]
					)
				)
				line_bot_api.reply_message(event.reply_token, pesan)

		if text == 'Cek film dong':
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(sender)+' mau cari film apa?'))
			perintah.update({sender:['Cari film imdb', time.time()]})

	except Exception as e:
		try:
			et, ev, tb = sys.exc_info()
			lineno = tb.tb_lineno
			fn = tb.tb_frame.f_code.co_filename
			if sender != owner:
				line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Oopps.. '+namaBot.capitalize()+' ada kesalahan kak :('),TextSendMessage(text='Tapi tenang kak, laporan kesalahan ini terkirim ke owner untuk diperbaiki ;D')])
			line_bot_api.push_message(owner, TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e))))
		except:
			line_bot_api.push_message(owner, TextSendMessage(text="Undescribeable error detected!!"))
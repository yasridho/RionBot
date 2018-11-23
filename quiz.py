import os
import re
import sys
import random
import time
import json

from acc import (line_bot_api, qz, handler, owner, namaBot)
from sesuatu import (panggil, film_quiz)
from datetime import datetime
from linebot.models import *

soal = {}

@handler.add(PostbackEvent)
def handle_postback(event):
	if isinstance(event.source, SourceGroup):
		kirim = event.source.sender_id
	elif isinstance(event.source, SourceRoom):
		kirim = event.source.room_id
	else:
		kirim = event.source.user_id
	
	sender = event.source.user_id
	
	try:
		if event.postback.data[0] == '/':
			data = event.postback.data[1:].split(" ",1)
			if len(data) > 1:
				cmd, args = data[0].lower(), data[1]
			else:
				cmd, args = data[0].lower(), ""

			if cmd == "main":
				pesan = TemplateSendMessage(
					alt_text='Kamu yakin?',
					template=ConfirmTemplate(
						text='Kamu akan diberikan beberapa soal yang berhubungan dengan film. Siapkah kamu menjawabnya?',
						actions=[
							PostbackAction(
								label='Siap',
								text='Siapp, siapa takut?',
								data='/quiz ready'
							),
							PostbackAction(
								label='Tidak',
								text='Belum, saya masih gatau apa-apa tentang film T_T',
								data='/quiz not ready'
							)
						]
					)
				)
				line_bot_api.reply_message(event.reply_token, pesan)

			elif cmd == 'quiz':
				if args == 'ready':
					pertanyaan = qz.child("pertanyaan").get().val()
					tanya = random.choice([i for i in pertanyaan])
					jawab = pertanyaan[tanya]["Jawaban"]
					film = pertanyaan[tanya]["Film"]
					soal.update({kirim:[tanya, jawab]})
					line_bot_api.reply_message(event.reply_token, film_quiz(tanya, film))
				else:
					line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kabarin kalau udah siap ya kak ;D'))
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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	if isinstance(event.source, SourceGroup):
		kirim = event.source.sender_id
	elif isinstance(event.source, SourceRoom):
		kirim = event.source.room_id
	else:
		kirim = event.source.user_id
	
	sender = event.source.user_id
	profil = line_bot_api.get_profile(sender)
	text = event.message.text

	if kirim in soal:
		pertanyaan, jawaban = soal[kirim]

		if text.lower() == jawaban.lower():
			pertanyaan = qz.child("pertanyaan").get().val()
			tanya = random.choice([i for i in pertanyaan])
			jawab = pertanyaan[tanya]["Jawaban"]
			film = pertanyaan[tanya]["Film"]
			soal.update({kirim:[tanya, jawab]})
			line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Kak '+panggil(sender)+' benar ;D'), film_quiz(tanya, film)])
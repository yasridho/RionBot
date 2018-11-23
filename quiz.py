import os
import re
import sys
import random
import time
import json

from acc import (line_bot_api, qz, handler)
from sesuatu import panggil
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
					pesan = FlexSendMessage(
						alt_text=tanya,
						contents=BubbleContainer(
							direction='ltr',
							body=BoxComponent(
								layout='vertical',
								contents=[
									TextComponent(
										text=film,
										size='xs',
										align='start',
										color='#989898'
									),
									TextComponent(
										text=tanya,
										margin='md',
										align='center',
										wrap=True
									)
								]
							),
							footer=BoxComponent(
								layout='horizontal',
								contents=[
									ButtonComponent(
										action=PostbackAction(
											label='Menyerah',
											text='Nyerah deh',
											data='/nyerah'
										),
										color='#ffffff',
										height='sm'
									)
								]
							),
							styles=BubbleStyle(
								footer=BlockStyle(
									background_color='#a33f3f'
								)
							)
						)
					)
					line_bot_api.reply_message(event.reply_token, pesan)
				else:
					line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kabarin kalau udah siap ya kak ;D'))

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
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(sender)+' benar ;D'))
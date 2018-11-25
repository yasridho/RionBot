import errno
import os
import sys, random, datetime, time, re

from datetime import datetime
from acc import (line_bot_api, namaBot, owner, handler)
from sesuatu import (search_movie_imdb, panggil)
from linebot.models import *


perintah = {}
pencarian = {}

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

			if cmd == 'imdb':
				cari, nomor = args.split(" ")
				cari = cari.replace('+',' ')
				batas = int(nomor)+9
				hasil = pencarian[cari]
				jhasil = len(hasil[cari]) - int(nomor)
				res = list()
				if jhasil > 10:
					for i in hasil[int(nomor)+1:batas]:
						res.append(i)
					res.append(
						BubbleContainer(
							body=BoxComponent(
								layout='vertical',
								spacing='sm',
								contents=[
									ButtonComponent(
										action=PostbackAction(
											label='Selanjutnya',
											text='Selain itu?',
											data='/imdb '+cari.replace(' ','+')+' '+str(batas)
										),
										flex=1,
										gravity='center'
									)
								]
							)
						)
					)
					hasil = res
				else:
					hasil = hasil[int(nomor)+1:]
				
				pesan = FlexSendMessage(
						alt_text='Hasil pencarian: '+cari,
						contents=CarouselContainer(
							contents=hasil
						)
					)
				line_bot_api.reply_message(event.reply_token, pesan)

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
	text = event.message.text

	try:

		if sender in perintah:
			komando, waktu = perintah[sender]

			if komando == 'Cari film imdb':
				line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Sebentar kak '+panggil(sender)+', '+namaBot.capitalize()+' sedang menyiapkan hasil pencarian ;)'))
				pencarian.update({text:[]})
				for i in search_movie_imdb(text):
					pencarian[text].append(i)
				hasil = pencarian[text]
				if len(hasil) > 10:
					hasil = hasil[:9]
					kirimin = list()
					for r in hasil:
						kirimin.append(r)
					kirimin.append(
						BubbleContainer(
							body=BoxComponent(
								layout='vertical',
								spacing='sm',
								contents=[
									ButtonComponent(
										action=PostbackAction(
											label='Selanjutnya',
											text='Selain itu?',
											data='/imdb '+text.replace(' ','+')+' 9'
										),
										flex=1,
										gravity='center'
									)
								]
							)
						)
					)
					pesan = FlexSendMessage(
						alt_text='Hasil pencarian: '+text,
						contents=CarouselContainer(
							contents=kirimin
						)
					)
				else:
					pesan = FlexSendMessage(
						alt_text='Hasil pencarian: '+text,
						contents=CarouselContainer(
							contents=hasil
						)
					)
				line_bot_api.push_message(sender, pesan)

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
import urllib
import errno
import os
import sys, random, datetime, time, re
import json
from linebot.models import *
from acc import (namaBot, line_bot_api, handler)
from sesuatu import download_film

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

			if cmd == 'next_download':
				cari, pengirim, nomor = args.split(" ")
				film = download_film(cari)
				jfilm = len(film) - int(nomor)
				batas = int(nomor)+9
				res = list()
				if jfilm > 10:
					for i in film[int(nomor)+1:batas]:
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
											data='/next_download '+cari+' '+kirim+' '+str(batas)
										),
										flex=1,
										gravity='center'
									)
								]
							)
						)
					)
				else:
					res = film[int(nomor)+1:]
				hasil = FlexSendMessage(
					alt_text='Hasil pencarian: '+cari.capitalize(),
					contents=CarouselContainer(
						contents=res
					)
				)
				line_bot_api.reply_message(event.reply_token, hasil)
	except Exception as e:
		try:
			et, ev, tb = sys.exc_info()
			lineno = tb.tb_lineno
			fn = tb.tb_frame.f_code.co_filename
			line_bot_api.push_message(kirim, TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e))))
		except:
			line_bot_api.push_message(kirim, TextSendMessage(text="Undescribeable error detected!!"))

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
	
	try:

		if kirim in perintah:
			komando, waktu = perintah[kirim]
			durasi = time.time() - waktu
			if durasi > 60:
				del perintah[kirim]
				return

			if komando == "Iya, mau nyari film":
				film = download_film(text)
				res = list()
				if len(film) > 10:
					for i in film[:9]:
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
											data='/next_download '+text+' '+kirim+' 9'
										),
										flex=1,
										gravity='center'
									)
								]
							)
						)
					)
				else:
					res = film
				hasil = FlexSendMessage(
					alt_text='Hasil pencarian: '+text.capitalize(),
					contents=CarouselContainer(
						contents=res
					)
				)
				line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=namaBot.capitalize()+' dapat ini kak '+profil.display_name), hasil])
				del perintah[sender]

		if text == "Iya, mau nyari film":
			perintah.update({sender:[text, time.time()]})
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Mau cari film apa?"))

		elif text == "Gada sih, cuma mau lihat-lihat film aja":
			perintah.update({sender:[text, time.time()]})

		elif text == "Mau download film":
			konfirmasi = BubbleContainer(
				direction='ltr',
				header=BoxComponent(
					layout='vertical',
					contents=[
						TextComponent(
							text='Ada film yang ingin kamu cari?',
							align='center'
						)
					]
				),
				footer=BoxComponent(
					layout='horizontal',
					contents=[
						BoxComponent(
							layout='horizontal',
							spacing='sm',
							contents=[
								ButtonComponent(
									action=MessageAction(
										label='Iya',
										text='Iya, mau nyari film'
									),
									style='primary'
								),
								ButtonComponent(
									action=MessageAction(
										label='Tidak',
										text='Gada sih, cuma mau lihat-lihat film aja'
									),
									style='secondary'
								)
							]
						)
					]
				)
			)
			line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='Kamu mau apa?',contents=konfirmasi))


	except Exception as e:
		try:
			et, ev, tb = sys.exc_info()
			lineno = tb.tb_lineno
			fn = tb.tb_frame.f_code.co_filename
			line_bot_api.push_message(kirim, TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e))))
		except:
			line_bot_api.push_message(kirim, TextSendMessage(text="Undescribeable error detected!!"))
import requests, json
import errno
import os
import sys, random, datetime, time, re
import tempfile
import urllib
import acc
import pafy

from threading import Timer
from sesuatu import *
from acc import (namaBot, google_key, line_bot_api, handler)
from linebot.exceptions import LineBotApiError
from linebot.models import *
from linebot.exceptions import (
	InvalidSignatureError
)

perintah = {} # menyimpan perintah agar dapat menerima inputan
#sesuatu = {}  # digunakan untuk menyimpan result
videos = {}

@handler.add(PostbackEvent)
def handle_postback(event):
	if isinstance(event.source, SourceGroup):
		kirim = event.source.sender_id
	elif isinstance(event.source, SourceRoom):
		kirim = event.source.room_id
	else:
		kirim = event.source.user_id
	
	try:

		if event.postback.data == 'test':
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Test berhasil"))
	
		if event.postback.data[0] == '/':
			data = event.postback.data[1:].split(" ",1)
			if len(data) > 1:
				cmd, args = data[0].lower(), data[1]
			else:
				cmd, args = data[0].lower(), ""

			if cmd == 'ytdownload':
				thumbnails, link = args.split(' ')
				download_ini = download(thumbnails, link)
				line_bot_api.reply_message(event.reply_token, download_ini)
			
			elif cmd == 'yt':
				data = args.split(" ",1)
				if len(data) > 1:
					mau, cari = data[0], data[1]
				else:
					mau, cari = data[0], ""
				
				if mau == 'iya':
					perintah.update({event.source.user_id:['Cari lagi', time.time()]})
					try:
						del videos[cari.replace('+',' ')]
					except:pass
				
				elif mau == 'tidak':
					line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Terima kasih ;)"))
					try:
						del videos[cari.replace('+',' ')]
					except:pass
				
				else:
					cari, nomor = args.split(" ")
					try:
						video = videos[cari.replace('+',' ')]
						batas = int(nomor) + 9
					except:
						videos.update({cari:[]})
						for i in youtube(cari):
							videos[cari].append(i)
						video = videos[cari.replace('+',' ')]
						batas = 19
					jvideo = 50 - int(nomor)
					res = list()
					if jvideo > 10:
						for i in video[int(nomor)+1:batas]:
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
												data='/yt '+cari+' '+str(batas)
											),
											flex=1,
											gravity='center'
										)
									]
								)
							)
						)
						video = res
					else:
						video = video[int(nomor)+1:]
					line_bot_api.reply_message(event.reply_token, [FlexSendMessage(alt_text='Hasil pencarian: '+cari,contents=CarouselContainer(contents=video)), TemplateSendMessage(alt_text='Mau cari video lagi?', template=ConfirmTemplate(text='Mau cari video lagi?',actions=[PostbackAction(label='Iya',text='Iya',data='/yt iya '+cari),PostbackAction(label='Tidak',text='Tidak',data='/yt tidak '+cari)]))])

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
	try:

		if isinstance(event.source, SourceGroup):
			kirim = event.source.sender_id
		elif isinstance(event.source, SourceRoom):
			kirim = event.source.room_id
		else:
			kirim = event.source.user_id

		sender = event.source.user_id

		def balas(args):
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text=args))

		def cbalas(args):
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text=args, quick_reply=[QuickReplyButton(action=MessageAction(label="YouTube Search", text="YouTube")),QuickReplyButton(action=MessageAction(label="Google Image Search", text="Google Image"))]))

		def message(args):
			line_bot_api.push_message(kirim, TextSendMessage(text=args))

		def cmessage(args):
			line_bot_api.push_message(kirim, TextSendMessage(text=args, quick_reply=[QuickReplyButton(action=MessageAction(label="YouTube Search", text="YouTube")),QuickReplyButton(action=MessageAction(label="Google Image Search", text="Google Image"))]))

		def img(args):
			line_bot_api.push_message(kirim, ImageSendMessage(
				original_content_url=args,
				preview_image_url=args))

		text = event.message.text

		if sender in perintah:
			komando, waktu = perintah[sender]
			
			if komando == "Mau nonton YouTube":
				try:
					line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Tunggu sebentar ya kak '+panggil(sender)+', '+namaBot.capitalize()+' sedang mengumpulkan data.. ;)'))
					videos.update({text:[]})
					for i in youtube(text):
						videos[text].append(i)
					hasil = videos[text][:9]
					cari = text.split()
					res = list()
					for i in hasil:
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
											data='/yt '+'+'.join(cari)+' 9'
										),
										flex=1,
										gravity='center'
									)
								]
							)
						)
					)
					line_bot_api.push_message(kirim, [FlexSendMessage(alt_text='Hasil pencarian: '+text,contents=CarouselContainer(contents=res)), TemplateSendMessage(alt_text='Mau cari video lagi?', template=ConfirmTemplate(text='Mau cari video lagi?',actions=[PostbackAction(label='Iya',text='Iya',data='/yt iya '+text),PostbackAction(label='Tidak',text='Tidak',data='/yt tidak '+text)]))])
				except Exception as e:
					try:
						et, ev, tb = sys.exc_info()
						lineno = tb.tb_lineno
						fn = tb.tb_frame.f_code.co_filename
						balas("[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
					except:
						balas("Undescribeable error detected!!")
				del perintah[sender]

			elif komando == 'Cari lagi':
				perintah.update({sender:['Mau nonton YouTube', time.time()]})
				line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Mau cari apa di YouTube?'))

			elif komando == "Google Image":
				try:
					line_bot_api.reply_message(event.reply_token, gis(text))
				except Exception as e:
					try:
						et, ev, tb = sys.exc_info()
						lineno = tb.tb_lineno
						fn = tb.tb_frame.f_code.co_filename
						balas("[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
					except:
						balas("Undescribeable error detected!!")
				del perintah[sender]

		elif text == "Mau nonton YouTube":
			perintah.update({sender:[text, time.time()]})
			balas("Mau cari apa di YouTube?")

		elif text == "=cmds" or text.lower() == "perintah":
			buttons_template = TemplateSendMessage(
				alt_text='Perintah-perintah',
				template=ButtonsTemplate(
					title='PERINTAH',
					text="Ini pilihan perintah yang bisa kamu pakai",
					actions=[
						MessageTemplateAction(
							label='Youtube Search',
							text='YouTube'
						),
						MessageTemplateAction(
							label='Google Image Search',
							text='Google Image'
						),
						MessageTemplateAction(
							label='Owner',
							text='Owner'
						)
					]
				)
			)
			line_bot_api.reply_message(event.reply_token, buttons_template)

		elif text[0] == "=" or "rion" in text:
			data = text[1:].split(" ",1)
			if len(data) > 1:
				cmd, args = data[0].lower(), data[1]
			else:
				cmd, args = data[0].lower(), ""


			############ COMMAND STARTS HERE ############

			if cmd == "yt":
				if args == "":
					balas("Type =yt <your keyword> to search a youtube video.")
					return
				try:
					line_bot_api.reply_message(event.reply_token, youtube(args))
				except:cbalas(args+" tidak ketemu di youtube :<")

			elif cmd == "gis":
				try:
					if args == "":
						balas("Type =gis <your keyword> to search an image.")
						return
					line_bot_api.reply_message(event.reply_token, gis(args))
						#message(judul+"\nSize: "+str(tinggi)+"x"+str(lebar)+"\nType: "+jenis+"\nSource: "+link)
				except Exception as e:
					try:
						et, ev, tb = sys.exc_info()
						lineno = tb.tb_lineno
						fn = tb.tb_frame.f_code.co_filename
						line_bot_api.reply_message(event.reply_token, TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e))))
					except:
						line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Undescribeable error detected!!"))

	except LineBotApiError as e:
		print(e.status_code)
		print(e.error.message)
		print(e.error.details)
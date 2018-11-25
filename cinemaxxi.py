import requests, json
import errno
import os
import sys, random, datetime, time, re
import tempfile
import urllib
import acc
import cinema21

from sesuatu import (tayang, info_film, panggil, bioskop_terdekat, ingetin, ingetin30)
from acc import (namaBot, google_key, line_bot_api, handler, db)
from threading import Timer
from datetime import datetime
from linebot.exceptions import LineBotApiError
from linebot.models import *
from linebot.exceptions import (
	InvalidSignatureError
)

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

			if cmd == 'cek_bioskop':
				line_bot_api.reply_message(event.reply_token, tayang(args))

			elif cmd == 'cek_film_bioskop':
				line_bot_api.reply_message(event.reply_token, info_film(args))

			elif cmd == 'reminder':
				jamku, judul, bioskop, tanggalku = args.split(" ")
				judul = judul.replace("+"," ")
				bioskop = bioskop.replace("+"," ")
				jam, menit = jamku.split(":")
				tgl, bln, thn = tanggalku.split("-")

				x = datetime.today()
				if int(thn) <= x.year:
					if int(bln) <= x.month:
						if int(tgl) <= x.day:
							if int(jam) <= x.hour:
								if int(menit) <= x.minute:
									line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Waktunya sudah lewat kak :('))
									return

				if x.hour < int(jam):
					ingat_jam = int(jam)
					ingat_menit = int(menit) - 30
					if ingat_menit < 0:
						ingat_jam = int(jam) - 1
						ingat_menit = abs(ingat_menit)
					r = x.replace(hour=x.hour+(ingat_jam-x.hour), minute=x.minute+(ingat_menit-x.minute))
					delta_b = r - x
					detik = delta_b.seconds+1
					b = Timer(detik, ingetin30, (event.source.user_id, jamku, judul, bioskop))
					b.start()
				
				y = x.replace(hour=x.hour+(int(jam)-x.hour), minute=x.minute+(int(menit)-x.minute))
				delta_t = y - x
				secs = delta_t.seconds+1
				t = Timer(secs, ingetin, (event.source.user_id, jamku, judul, bioskop))
				t.start()
				line_bot_api.reply_message(event.reply_token, TextSendMessage('Okee kak ;D'))
				data = {'tanggal':tanggalku,'jam':jamku,'ulang':False}
				db.child("pengguna").child(event.source.user_id).child("tambahan").child("pengingat").child('Nonton '+judul.capitalize()+' di '+bioskop).set(data)

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


# CEK LOKASI PENGGUNA
@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
	if isinstance(event.source, SourceGroup):
		kirim = event.source.sender_id
	elif isinstance(event.source, SourceRoom):
		kirim = event.source.room_id
	else:
		kirim = event.source.user_id

	sender = event.source.user_id
	
	# MENGAMBIL INPUTAN PENGGUNA
	if sender in perintah:
		komando, waktu = perintah[sender]

		# MENAMPILKAN BIOSKOP TERDEKAT
		if komando == "Cek bioskop terdekat":
			try:
				line_bot_api.reply_message(event.reply_token, bioskop_terdekat(event.message.latitude, event.message.longitude))
				data = {'nama_lokasi':event.message.address,
						'latitude':event.message.latitude,
						'longitude':event.message.longitude}
				db.child("pengguna").child(sender).child("tambahan").child("lokasi").set(data)
				del perintah[sender]
			except:
				try:
					balasCepat = list()
					cinema = cinema21.Cinema21()
					for y in cinema.cities()[0]:
						balasCepat.append(
							QuickReplyButton(
								action=MessageAction(
									label=y[1].capitalize(),
									text=y[1].capitalize()
								)
							)
						)
					line_bot_api.reply_message(event.reply_token,
						[TextSendMessage(text=namaBot.capitalize()+' tidak dapat menemukan bioskop terdekat kak :('),
						TextSendMessage(text='Kakak sekarang di kota apa?',quick_reply=QuickReply(items=balasCepat[:13]))]
					)
					del perintah[sender]
					perintah.update({sender:["Cek bioskop", time.time()]})
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
	try:

		if isinstance(event.source, SourceGroup):
			kirim = event.source.sender_id
		elif isinstance(event.source, SourceRoom):
			kirim = event.source.room_id
		else:
			kirim = event.source.user_id

		sender = event.source.user_id

		text = event.message.text

		# MENGAMBIL INPUTAN PENGGUNA
		if sender in perintah:
			komando, waktu = perintah[sender]

			# MENAMPILKAN BIOSKOP DI KOTA
			if komando == "Cek bioskop":
				try:
					cinema = cinema21.Cinema21()
					kota = text.lower()
					for y in cinema.cities()[0]:
						if kota == y[1].lower():
							kode = y[0]
					terdekat = cinema.city_cinemas(kode)
					premiere = terdekat[0]
					xxi = terdekat[1]
					imax = terdekat[2]
					res = list()
				
					if len(premiere) > 0:
						for film in premiere:
							bioskop = film[4]
							kode = film[0]
							keterangan = film[6].replace('\r','')
							res.append(
								BubbleContainer(
									header=BoxComponent(
										layout='vertical',
										contents=[
											TextComponent(
												text=bioskop,
												size='lg',
												align='center',
												weight='bold',
												color='#f4f4f4',
												wrap=True
											)
										]
									),
									hero=ImageComponent(
										url='https://i.postimg.cc/28r8Vsnt/premiere.png',
										size='full',
										aspect_ratio='3:1',
										aspect_mode='cover'
									),
									body=BoxComponent(
										layout='vertical',
										contents=[
											TextComponent(
												text=keterangan,
												margin='lg',
												size='sm',
												align='center',
												color='#e4e4e4',
												wrap=True
											)
										]
									),
									footer=BoxComponent(
										layout='horizontal',
										contents=[
											ButtonComponent(
												action=PostbackAction(
													text='Mau liat film di '+bioskop.capitalize()+' dong',
													label='Lihat Film',
													data='/cek_bioskop '+kode
												),
												color='#860000',
												style='primary'
											)
										]
									),
									styles=BubbleStyle(
										header=BlockStyle(
											background_color='#000000'
										),
										body=BlockStyle(
											background_color='#000000'
										),
										footer=BlockStyle(
											background_color='#000000'
										)
									)
								)
							)

					if len(xxi) > 0:
						for film in xxi:
							bioskop = film[4]
							kode = film[0]
							keterangan = film[6].replace('\r','')
							res.append(
								BubbleContainer(
									header=BoxComponent(
										layout='vertical',
										contents=[
											TextComponent(
												text=bioskop,
												size='lg',
												align='center',
												weight='bold',
												color='#f4f4f4',
												wrap=True
											)
										]
									),
									hero=ImageComponent(
										url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTiTQHHaE05tNJ7cNhMbE6DmB0EXBHe0HnbRULKt0YpG9-uc5v5',
										size='full',
										aspect_ratio='3:1',
										aspect_mode='cover'
									),
									body=BoxComponent(
										layout='vertical',
										contents=[
											TextComponent(
												text=keterangan,
												margin='lg',
												size='sm',
												align='center',
												color='#e4e4e4',
												wrap=True
											)
										]
									),
									footer=BoxComponent(
										layout='horizontal',
										contents=[
											ButtonComponent(
												action=PostbackAction(
													text='Mau liat film di '+bioskop.capitalize()+' dong',
													label='Lihat Film',
													data='/cek_bioskop '+kode
												),
												color='#860000',
												style='primary'
											)
										]
									),
									styles=BubbleStyle(
										header=BlockStyle(
											background_color='#000000'
										),
										body=BlockStyle(
											background_color='#000000'
										),
										footer=BlockStyle(
											background_color='#000000'
										)
									)
								)
							)
					if len(imax) > 0:
						for film in imax:
							bioskop = film[4]
							kode = film[0]
							keterangan = film[6].replace('\r','')
							res.append(
								BubbleContainer(
									header=BoxComponent(
										layout='vertical',
										contents=[
											TextComponent(
												text=bioskop,
												size='lg',
												align='center',
												weight='bold',
												color='#f4f4f4',
												wrap=True
											)	
										]
									),
									hero=ImageComponent(
										url='https://i.postimg.cc/nLY3cQxg/imax.png',
										size='full',
										aspect_ratio='3:1',
										aspect_mode='cover'
									),
									body=BoxComponent(
										layout='vertical',
										contents=[
											TextComponent(
												text=keterangan,
												margin='lg',
												size='sm',
												align='center',
												color='#e4e4e4',
												wrap=True
											)
										]
									),
									footer=BoxComponent(
										layout='horizontal',
										contents=[
											ButtonComponent(
												action=PostbackAction(
													text='Mau liat film di '+bioskop.capitalize()+' dong',
													label='Lihat Film',
													data='/cek_bioskop '+kode
												),
												color='#860000',
												style='primary'
											)
										]
									),
									styles=BubbleStyle(
										header=BlockStyle(
											background_color='#000000'
										),
										body=BlockStyle(
											background_color='#000000'
										),
										footer=BlockStyle(
											background_color='#000000'
										)
									)
								)
							)
					hasil = FlexSendMessage(
						alt_text="Bioskop di "+text,
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
						if sender != owner:
							line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Oopps.. '+namaBot.capitalize()+' ada kesalahan kak :('),TextSendMessage(text='Tapi tenang kak, laporan kesalahan ini terkirim ke owner untuk diperbaiki ;D')])
						line_bot_api.push_message(owner, TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e))))
					except:
						line_bot_api.push_message(owner, TextSendMessage(text="Undescribeable error detected!!"))
				del perintah[sender]

		# CHAT BIASA
		if text == "Cek film bioskop":
			data = db.child("pengguna").get().val()[sender]
			try:
				lokasi = data["tambahan"]["lokasi"]
				lat = lokasi["latitude"]
				lng = lokasi["longitude"]
				line_bot_api.push_message(kirim, bioskop_terdekat(lat, lng))
			except:
				perintah.update({sender:['Cek bioskop terdekat', time.time()]})
				line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Share lokasi dulu kak "+panggil(sender)+", nanti kucarikan bioskop terdekat ;)", quick_reply=QuickReply(items=[QuickReplyButton(action=LocationAction(label='Share lokasi'))])))

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
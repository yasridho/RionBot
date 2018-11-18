import sesuatu
import os
import time
import sys

from datetime import datetime
from threading import Timer
from sesuatu import (panggil, bulan)
from acc import (namaBot, google_key, line_bot_api, handler, db)
from linebot.models import *

remind_me = {}

@handler.add(PostbackEvent)
def handle_postback(event):
	sender = event.source.user_id
	try:
		if event.postback.data[0] == '/':
			data = event.postback.data[1:].split(" ",1)
			if len(data) > 1:
				cmd, args = data[0].lower(), data[1]
			else:
				cmd, args = data[0].lower(), ""

			if cmd == "pengingat":
				sekarang = datetime.today()
				if sekarang.minute < 10:
					menit = '0'+str(sekarang.minute)
				else:
					menit = str(sekarang.minute)
				if sekarang.hour < 10:
					jam = '0'+str(sekarang.hour)
				else:
					jam = str(sekarang.hour)
				pesan = TemplateSendMessage(
					alt_text='Liat pengingat atau mau nambahin pengingat?',
					template=ButtonsTemplate(
						title='Pengingat',
						text='Mau cek atau nambahin pengingat?',
						actions=[
							PostbackAction(
								label='Cek Pengingat',
								text='Mau cek pengingat',
								data='/cek_pengingat'
							),
							DatetimePickerAction(
								label='Tambah pengingat',
								text='Mau nambahin pengingat',
								data='/tambah_pengingat',
								mode='datetime',
								initial=str(sekarang.year)+'-'+str(sekarang.month)+'-'+str(sekarang.day+1)+'t'+jam+':'+menit,
								min=str(sekarang.date())+'t'+jam+':'+menit
							)
						]
					)
				)
				line_bot_api.reply_message(event.reply_token, pesan)

			elif cmd == 'tambah_pengingat':
				kalender = event.postback.params['datetime']
				remind_me.update({sender:kalender})
				tanggal, jamku = kalender.split("T")
				tgl, bln, thn = tanggal.split('-')
				line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(sender)+' mau diingatkan apa pada tanggal '+tgl+' bulan '+bulan(int(bln))+' tahun '+thn+' jam '+jamku+'?'))

			elif cmd == 'cek_pengingat':
				try:
					kumpulan = list()
					reminder = db.child("pengguna").child(sender).child("tambahan").child("pengingat").get().val()
					for alarm in reminder:
						kumpulan.append(
							BoxComponent(
								layout='baseline',
								margin='sm',
								contents=[
									TextComponent(
										text=alarm["jam"],
										size='xs',
										align='start'
									),	
									TextComponent(
										text=alarm["tanggal"],
										size='xs',
										align='center'
									),
									TextComponent(
										text=alarm,
										size='xs',
										align='end',
										wrap=True
									)
								]
							)
						)
					jadwal = BubbleContainer(
						direction='ltr',
						header=BoxComponent(
							layout='vertical',
							contents=[
								TextComponent(
									text='PENGINGAT',
									align='center',
									weight='bold',
									color='#aaaaaa'
								)
							]
						),
						hero=ImageComponent(
							url=line_bot_api.get_profile(sender).picture_url,
							size='full',
							aspect_ratio='4:3',
							aspect_mode='cover'
						),
						body=BoxComponent(
							layout='vertical',
							contents=[
								TextComponent(
									text='Berikut ini pengingat kak '+panggil(sender),
									size='sm',
									align='start',
									gravity='top'
								),
								SeparatorComponent(margin='lg'),
								BoxComponent(
									layout='vertical',
									margin='sm',
									contents=[
										BoxComponent(
											layout='baseline',
											contents=[
												TextComponent(
													text='Jam',
													size='xs',
													align='start'
												),
												TextComponent(
													text='Tanggal',
													size='xs',
													align='center'
												),
												TextComponent(
													text='Agenda',
													size='xs',
													align='end'
												)
											]
										),
										SeparatorComponent(margin='xs'),
										BoxComponent(
											layout='vertical',
											margin='sm',
											contents=kumpulan
										)
									]
								)
							]	
						),
						footer=BoxComponent(
							layout='horizontal',
							contents=[
								ButtonComponent(
									action=PostbackAction(
										label='Tambah Pengingat',
										text='Mau nambah pengingat',
										data='/tambah_pengingat'
									),
									color='#ffffff',
									height='sm'
								)
							]
						),
						styles=BubbleStyle(
							footer=BlockStyle(
								background_color='#00318d'
							)
						)
					)
					kirim = FlexSendMessage(
						alt_text='Pengingat',
						contents=jadwal
					)
					line_bot_api.reply_message(event.reply_token, kirim)
				except:
					line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kamu tidak memiliki pengingat.'))
	except Exception as e:
		try:
			et, ev, tb = sys.exc_info()
			lineno = tb.tb_lineno
			fn = tb.tb_frame.f_code.co_filename
			line_bot_api.push_message(sender, TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e))))
		except:
			line_bot_api.push_message(sender, TextSendMessage(text="Undescribeable error detected!!"))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	sender = event.source.user_id
	text = event.message.text
	if sender in remind_me:
		kalender = remind_me[sender]
		tanggal, jamku = kalender.split("T")
		data = {'tanggal':tanggal,'jam':jamku,'ulang':False}
		db.child("pengguna").child(sender).child("tambahan").child("pengingat").child(text).set(data)
		line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Okee kak ;D'))
		sesuatu.reminder()
		del remind_me[sender]
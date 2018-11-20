import sesuatu
import os
import time
import sys

from datetime import datetime
from threading import Timer
from sesuatu import (panggil, bulan, indozone)
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
				try:
					data = db.child("pengguna").child(sender).child("tambahan").get().val()
					zona = data["zona_waktu"]
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
				except:
					line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Kak '+panggil(sender)+' belum menentukan zona waktu, silahkan dipilih dulu ;D'), indozone()])

			elif cmd == 'zona':
				try:
					sekarang = db.child("pengguna").child(sender).child("tambahan").child("zona_waktu").get().val()
				except:
					sekarang = ""

				if not sekarang == "":
					if args != sekarang:
						konfirm = TemplateSendMessage(
							alt_text='Kamu ingin mengubah zona waktu kamu?',
							template=ConfirmTemplate(
								text='Kamu ingin mengubah zona waktu kamu dari '+sekarang+' ke '+args.upper()+'?',
								actions=[
									PostbackAction(
										label='Iya',
										text='Iya',
										data='/ubah_zona_waktu '+args
									),
									PostbackAction(
										label='Tidak',
										text='Tidak',
										data='/ubah_zona_waktu tidak'
									)
								]
							)
						)
						line_bot_api.reply_message(event.reply_token, konfirm)
					else:
						line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Zona waktu kak '+panggil(sender)+' sudah '+args.upper()+' :|'))
				else:
					db.child("pengguna").child(sender).child("tambahan").child("zona_waktu").set(args.upper())
					line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Zona waktu kak '+panggil(sender)+' berhasil diset ;D'))
					if sender in remind_me:
						status, kalender = remind_me[sender]
						if status == 'pending':
							t_timestamp = time.mktime(datetime.strptime(kalender, "%Y-%m-%dT%H:%M").timetuple())
							MENIT 		= 60
							JAM 		= MENIT * 60
							if args.upper() == 'WITA':
								t_timestamp += (1*JAM)
							elif args.upper() == 'WIT':
								t_timestamp += (2*JAM)
							durasi = t_timestamp - time.time()
							if int(durasi) <= 20:
								line_bot_api.push_message(sender, [TextSendMessage(text='Maaf kak '+panggil(sender)+', waktunya udah lewat :('),TextSendMessage(text='Silahkan pilih waktu lagi ;D')])
								del remind_me[sender]
							else:
								remind_me.update({sender:['sukses',kalender]})
								line_bot_api.push_message(sender, TextSendMessage(text='Kak '+panggil(sender)+' mau diingatkan apa pada tanggal '+tgl+' bulan '+bulan(int(bln))+' tahun '+thn+' jam '+jamku+'?'))

			elif cmd == 'zona_waktu':
				line_bot_api.reply_message(event.reply_token, indozone())

			elif cmd == 'ubah_zona_waktu':
				try:
					sekarang = db.child("pengguna").child(sender).child("tambahan").child("zona_waktu").get().val()
					if args != 'tidak':
						if sekarang.lower() == args:
							line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Kak "+panggil(sender)+" sudah "+args.upper()+" :|"))
						else:
							db.child("pengguna").child(sender).child("tambahan").child("zona_waktu").update(args.upper())
							line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Zona waktu kak '+panggil(sender)+' berhasil diubah menjadi '+args.upper()+' ;D'))
					else:
						line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Zona waktu kak '+panggil(sender)+' tetap '+sekarang+' ;D'))
				except:
					line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Kak '+panggil(sender)+' belum menentukan zona waktu :('), TextSendMessage(text='Silahkan pilih zona waktu terlebih dahulu ;D'), indozone()])

			elif cmd == 'tambah_pengingat':
				kalender = event.postback.params['datetime']
				t_timestamp = time.mktime(datetime.strptime(kalender, "%Y-%m-%dT%H:%M").timetuple())
				durasi = t_timestamp - time.time()
				if int(durasi) <= 0:
					line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Maaf kak '+panggil(sender)+', waktunya udah lewat :('),TextSendMessage(text='Silahkan pilih waktu lagi ;D')])
					return
				try:
					status = 'sukses'
					data = db.child("pengguna").child(sender).child("tambahan").get().val()
					zona_waktu = data["zona_waktu"]
					tanggal, jamku = kalender.split("T")
					thn, bln, tgl = tanggal.split('-')
					line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(sender)+' mau diingatkan apa pada tanggal '+tgl+' bulan '+bulan(int(bln))+' tahun '+thn+' jam '+jamku+'?'))
				except:
					status = 'pending'
					line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Maaf kak, kak '+panggil(sender)+' belum memberitahu zona waktu kakak :('), TextSendMessage(text='Silahkan dipilih dulu kak ;D'), indozone()])

				remind_me.update({sender:[status,kalender]})

			elif cmd == 'cek_pengingat':
				try:
					sekarang = datetime.today()
					if sekarang.minute < 10:
						menit = '0'+str(sekarang.minute)
					else:
						menit = str(sekarang.minute)
					if sekarang.hour < 10:
						jam = '0'+str(sekarang.hour)
					else:
						jam = str(sekarang.hour)
					kumpulan = list()
					reminder = db.child("pengguna").child(sender).child("tambahan").child("pengingat").get().val()
					for alarm in reminder:
						kumpulan.append(
							BoxComponent(
								layout='baseline',
								margin='sm',
								contents=[
									TextComponent(
										text=reminder[alarm]["jam"],
										size='xs',
										align='start'
									),	
									TextComponent(
										text=reminder[alarm]["tanggal"],
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
									action=DatetimePickerAction(
										label='Tambah pengingat',
										text='Mau nambahin pengingat',
										data='/tambah_pengingat',
										mode='datetime',
										initial=str(sekarang.year)+'-'+str(sekarang.month)+'-'+str(sekarang.day+1)+'t'+jam+':'+menit,
										min=str(sekarang.date())+'t'+jam+':'+menit
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
		status, kalender = remind_me[sender]
		if status == 'sukses':
			tanggal, jamku = kalender.split("T")
			thn, bln, tgl = tanggal.split("-")
			tanggal = tgl+'-'+bln+'-'+thn
			data = {'tanggal':tanggal,'jam':jamku,'ulang':False}
			db.child("pengguna").child(sender).child("tambahan").child("pengingat").child(text).set(data)
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Okee kak ;D'))
			sesuatu.reminder()
			del remind_me[sender]
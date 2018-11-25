import requests, json
import sys
import os
import random
import re
import urllib
import pafy
import time
import cinema21
from linebot.models import *
from acc import (google_key, db, line_bot_api, qz)
from datetime import datetime
from threading import Timer
from calendar import monthrange
from imdb import IMDb

running_notif = {}

def ukuran_file(args):
	minimal = 2**10
	n = 0
	ukuran = {0:'', 1:'Kilo', 2:'Mega', 3:'Giga', 4:'Tera'}
	while args > minimal:
		args = args/minimal
		n = n + 1
	if args == 1:
		return args, ukuran[n]+'byte'
	else:
		return args, ukuran[n]+'bytes'

def bulan(args):
	data = {1:'Januari',2:'Februari',3:'Maret',4:'April',5:'Mei',6:'Juni',7:'Juli',8:'Agustus',9:'September',10:'Oktober',11:'November',12:'Desember'}
	return data[args]

def panggil(args):
	try:
		data = db.child("pengguna").get().val()[args]
		try:
			panggilan = data["tambahan"]["panggilan"]
			return panggilan
		except:
			return data["nama"]
	except:pass

def mulai_permainan():
	pesan = TemplateSendMessage(
		alt_text='Permainan belum dibuka :(',
		template=ButtonsTemplate(
			actions=[
				PostbackAction(
					label='Buka Permainan',
					text='Main kuy',
					data='/quiz ready'
				)
			],
			title='Oooppps...',
			text='Permainan belum dibuka, silahkan klik tombol dibawah'
		)
	)
	return pesan

def hasil_akhir(nama, jumlah_soal, total_poin, skorlist):
	yeezy = {}
	for player in skorlist:
		poin, waktu = skorlist[player]
		yeezy.update({player:poin})
	s = [(k, yeezy[k]) for k in sorted(yeezy, key=yeezy.get, reverse=True)]
	skors = list()
	num = 1
	for pemain, skor in s:
		nama_pemain = line_bot_api.get_profile(pemain).display_name
		skors.append(
			BoxComponent(
				layout='baseline',
				spacing='md',
				margin='sm',
				contents=[
					TextComponent(
						text=str(num),
						flex=0,
						size='xs'
					),
					TextComponent(
						text=nama_pemain,
						size='xs',
						align='start',
						wrap=True
					),
					TextComponent(
						text=str(skor)+'p',
						size='xs',
						align='end',
						wrap=False
					)
				]
			)
		)
		num += 1
	pesan = FlexSendMessage(
		alt_text='Hasil Akhir',
		contents=BubbleContainer(
			direction='ltr',
			header=BoxComponent(
				layout='vertical',
				contents=[
					TextComponent(
						text='Hasil',
						align='center',
						weight='bold',
						color='#ffffff'
					)
				]
			),
			body=BoxComponent(
				layout='vertical',
				contents=[
					TextComponent(
						text=nama,
						align='center'
					),
					TextComponent(
						text=str(jumlah_soal)+' soal terjawab',
						size='sm',
						align='center'
					),
					SeparatorComponent(
						margin='md'
					),
					BoxComponent(
						layout='baseline',
						spacing='md',
						margin='sm',
						contents=[
							TextComponent(
								text='Poin yang terkumpul',
								flex=0,
								size='sm'
							),
							TextComponent(
								text=str(total_poin-jumlah_soal),
								size='sm',
								align='end'
							),
							TextComponent(
								text='+ '+str(jumlah_soal),
								flex=0,
								size='xxs',
								color='#009b0e'
							),
							TextComponent(
								text='poin',
								size='sm'
							)
						]
					),
					BoxComponent(
						layout='baseline',
						margin='sm',
						contents=[
							TextComponent(
								text='Total',
								flex=3,
								size='sm',
								align='end',
								weight='bold',
								color='#777777'
							),
							TextComponent(
								text=str(total_poin)+' poin',
								size='sm',
								align='end',
								color='#071ffd'
							)
						]
					),
					SeparatorComponent(
						margin='sm'
					),
					TextComponent(
						text='Skor Tertinggi',
						margin='sm',
						size='xs',
						align='center',
						weight='bold',
						color='#777777'
					),
					SeparatorComponent(
						margin='sm'
					),
					BoxComponent(
						layout='vertical',
						margin='sm',
						contents=skors
					)
				]
			),
			footer=BoxComponent(
				layout='horizontal',
				contents=[
					ButtonComponent(
						action=PostbackAction(
							label='Main lagi',
							text='Main lagi dong',
							data='/quiz ready'
						),
						color='#ffffff',
						height='sm'
					)
				]
			),
			styles=BubbleStyle(
				header=BlockStyle(
					background_color='#14a6b7'
				),
				footer=BlockStyle(
					background_color='#14a6b7'
				)
			)
		)	
	)
	return pesan

def skor_akhir(data):
	skor = list()
	for nama in data:
		skor.append(
			BoxComponent(
				layout='baseline',
				margin='sm',
				contents=[
					TextComponent(
						text=nama,
						size='xs',
						align='center'
					),
					TextComponent(
						text=str(data[nama]),
						size='xs',
						align='center'
					)
				]
			)
		)
	pesan = FlexSendMessage(
		alt_text='Skor Permainan',
		contents=BubbleContainer(
			direction='ltr',
			header=BoxComponent(
				layout='vertical',
				contents=[
					TextComponent(
						text='Skor Permainan',
						align='center',
						weight='bold',
						color='#ffffff'
					)
				]
			),
			body=BoxComponent(
				layout='vertical',
				contents=[
					SeparatorComponent(),
					BoxComponent(
						layout='baseline',
						margin='xs',
						contents=[
							TextComponent(
								text='Nama',
								size='xs',
								align='center',
								weight='bold',
								color='#777777'
							),
							TextComponent(
								text='Skor',
								size='xs',
								align='center',
								weight='bold',
								color='#777777'
							)
						]
					),
					SeparatorComponent(),
					BoxComponent(
						layout='vertical',
						margin='sm',
						contents=skor
					)
				]
			),
			styles=BubbleStyle(
				header=BlockStyle(
					background_color='#14a6b7'
				)
			)
		)
	)
	return pesan

def pemain(aturan):
	num = 0
	peraturan = list()
	for atur in aturan:
		peraturan.append(
			BoxComponent(
				layout='baseline',
				contents=[
					TextComponent(
						text=str(num+1),
						size='xs'
					),
					TextComponent(
						text=atur,
						flex=10,
						size='xs',
						wrap=True
					)
				]
			)
		)
		num += 1
	peraturan.append(
		TextComponent(
			text='Tekan tombol dibawah untuk bergabung dalam permainan ;D',
			margin='md',
			size='xs',
			wrap=True
		)
	)
	pesan = FlexSendMessage(
		alt_text='Aturan Permainan',
		contents=BubbleContainer(
			direction='ltr',
			header=BoxComponent(
				layout='vertical',
				contents=[
					TextComponent(
						text='Aturan Permainan',
						align='center',
						weight='bold'
					)
				]
			),
			body=BoxComponent(
				layout='vertical',
				contents=peraturan
			),
			footer=BoxComponent(
				layout='horizontal',
				contents=[
					ButtonComponent(
						action=PostbackAction(
							label='Dimengerti',
							data='/join '+str(time.time())
						)
					)
				]
			)
		)
	)
	return pesan

def film_quiz(nomor, pertanyaan, film, pilihan, gambar):
	random.shuffle(pilihan)
	if gambar != "":
		pesan = FlexSendMessage(
			alt_text=pertanyaan,
			contents=BubbleContainer(
				direction='ltr',
				header=BoxComponent(
					layout='vertical',
					contents=[
						TextComponent(
							text=nomor,
							align='center',
							weight='bold',
							color='#8a8a8a'
						)
					]
				),
				hero=ImageComponent(
					url=gambar,
					size='full',
					aspect_ratio='1.51:1',
					aspect_mode='cover'
				),
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
							text=pertanyaan,
							margin='md',
							align='center',
							wrap=True
						),
						BoxComponent(
							layout='vertical',
							margin='md',
							spacing='sm',
							contents=[
								ButtonComponent(
									color='#283ACB',
									height='sm',
									style='primary',
									action=PostbackAction(
										label=pilihan[0],
										data='/jawab '+pilihan[0]
									)
								),
								ButtonComponent(
									color='#283ACB',
									height='sm',
									style='primary',
									action=PostbackAction(
										label=pilihan[1],
										data='/jawab '+pilihan[1]
									)
								),
								ButtonComponent(
									color='#283ACB',
									height='sm',
									style='primary',
									action=PostbackAction(
										label=pilihan[2],
										data='/jawab '+pilihan[2]
									)
								),
								ButtonComponent(
									color='#283ACB',
									height='sm',
									style='primary',
									action=PostbackAction(
										label=pilihan[3],
										data='/jawab '+pilihan[3]
									)
								)
							]
						),
						SpacerComponent(
							size='xxl'
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
	else:
		pesan = FlexSendMessage(
			alt_text=pertanyaan,
			contents=BubbleContainer(
				direction='ltr',
				header=BoxComponent(
					layout='vertical',
					contents=[
						TextComponent(
							text=nomor,
							align='center',
							weight='bold',
							color='#8a8a8a'
						)
					]
				),
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
							text=pertanyaan,
							margin='md',
							align='center',
							wrap=True
						),
						BoxComponent(
							layout='vertical',
							margin='md',
							spacing='sm',
							contents=[
								ButtonComponent(
									color='#283ACB',
									height='sm',
									style='primary',
									action=PostbackAction(
										label=pilihan[0],
										data='/jawab '+pilihan[0]
									)
								),
								ButtonComponent(
									color='#283ACB',
									height='sm',
									style='primary',
									action=PostbackAction(
										label=pilihan[1],
										data='/jawab '+pilihan[1]
									)
								),
								ButtonComponent(
									color='#283ACB',
									height='sm',
									style='primary',
									action=PostbackAction(
										label=pilihan[2],
										data='/jawab '+pilihan[2]
									)
								),
								ButtonComponent(
									color='#283ACB',
									height='sm',
									style='primary',
									action=PostbackAction(
										label=pilihan[3],
										data='/jawab '+pilihan[3]
									)
								)
							]
						),
						SpacerComponent(
							size='xxl'
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
	return pesan

def pesan_pengingat(kepada, pesan, agenda):
	line_bot_api.push_message(kepada, TextSendMessage(text=pesan))
	zona_waktu 	= db.child("pengguna").child(kepada).child("tambahan").child("zona_waktu").get().val()
	pengingat 	= db.child("pengguna").child(kepada).child("tambahan").child("pengingat").get().val()
	waktu 		= pengingat[agenda]["jam"]
	tanggal 	= pengingat[agenda]["tanggal"]
	waktu_alarm = tanggal+" "+waktu
	t_timestamp = time.mktime(datetime.strptime(waktu_alarm, "%d-%m-%Y %H:%M").timetuple())
	MENIT 		= 60
	JAM 		= MENIT * 60
	if zona_waktu == 'WITA':
		t_timestamp += (1*JAM)
	elif zona_waktu == 'WIT':
		t_timestamp += (2*JAM)
	durasi = t_timestamp - time.time()
	if int(durasi) <= 0:
		db.child("pengguna").child(kepada).child("tambahan").child("pengingat").child(agenda).remove()
		running_notif[kepada].remove(agenda)

def reminder():
	data = db.child("pengguna").get().val()
	for user in data:
		if not user in running_notif and not user == "total":
			running_notif.update({user:[]})
		if not user == "total":
			try:
				pengingat = data[user]["tambahan"]["pengingat"]
				zona_waktu = data[user]["tambahan"]["zona_waktu"]
				for alarm in pengingat:
					if alarm in running_notif[user]:continue
					waktu 		= pengingat[alarm]["jam"]
					tanggal 	= pengingat[alarm]["tanggal"]
					waktu_alarm = tanggal+" "+waktu
					t_timestamp = time.mktime(datetime.strptime(waktu_alarm, "%d-%m-%Y %H:%M").timetuple())
					x 			= datetime.today()

					durasi = t_timestamp - time.time()

					MENIT 		= 60
					JAM 		= MENIT * 60
					HARI 		= JAM * 24
					BULAN 		= monthrange(x.year, x.month)[1]
					TAHUN 		= BULAN * 12
					
					tahun 		= int(durasi / TAHUN)
					bulan 		= int((durasi % TAHUN) / BULAN)
					hari 		= int((durasi % BULAN) / HARI)
					jam 		= int((durasi % HARI) / JAM)
					menit 		= int((durasi % JAM) / MENIT)

					if zona_waktu 	== 'WITA':
						durasi = durasi + (1*JAM)
					elif zona_waktu == 'WIT':
						durasi = durasi + (2*JAM)
					
					running_notif[user].append(alarm)
					
					if int(durasi) <= 0:
						db.child("pengguna").child(user).child("tambahan").child("pengingat").child(alarm).remove()
				
					if menit >= 30:
						teks = 'Kak '+panggil(user)+' punya kegiatan 30 menit lagi ;D'
						durasi30 = durasi - (30*MENIT)
						b = Timer(durasi30, pesan_pengingat, (user, teks, alarm))
						b.start()

					if hari >= 1:
						teks = 'Kak '+panggil(user)+' besok punya kegiatan: '+alarm
						durasi1 = durasi - (1*HARI)
						b = Timer(durasi1, pesan_pengingat, (user, teks, alarm))
						b.start()

					teks = 'Kak '+panggil(user)+' punya jadwal hari ini: '+alarm
					t = Timer(durasi, pesan_pengingat, (user, teks, alarm))
					t.start()
			except:pass

def ingetin(pengirim, jam, film, bioskop):
	line_bot_api.push_message(pengirim,[
		TextSendMessage(
			text='Sudah jam '+jam+' kak '+panggil(pengirim)),
		TextSendMessage(
			text='Film '+film.capitalize()+' telah dimulai...'),
		TextSendMessage(
			text='Bagi anda yang memiliki karcis, dipersilahkan memasuki ruangan teater di '+bioskop+' ;)')])

def ingetin30(pengirim, jam, film, bioskop):
	line_bot_api.push_message(pengirim,[
		TextSendMessage(
			text='Kak '+panggil(pengirim)+'..'),
		TextSendMessage(
			text='Mau ngingetin kalau 30 menit lagi film '+film.capitalize()+' main kak '),
		TextSendMessage(
			text='Sebaiknya langsung ke bioskop '+bioskop+' biar g kelewatan nonton '+film+' ya kak ;D')])

def bioskop_terdekat(latitude, longitude):
	try:
		cinema = cinema21.Cinema21()
		terdekat = cinema.nearest_cinemas(latitude, longitude)
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
			alt_text="Bioskop dekat kamu",
			contents=CarouselContainer(
				contents=res
			)	
		)
		
		return hasil
	except Exception as e:
		try:
			et, ev, tb = sys.exc_info()
			lineno = tb.tb_lineno
			fn = tb.tb_frame.f_code.co_filename
			return TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
		except:
			return TextSendMessage(text="Undescribeable error detected!!")

def indozone():
	pilih = TemplateSendMessage(
		alt_text='Pilih zona waktu',
		template=ButtonsTemplate(
			title='Zona Waktu Indonesia',
			text='Pilih zona waktu kamu ;)',
			actions=[
				PostbackAction(
					label='WIB',
					text='Waktu Indonesia Barat',
					data='/zona wib'
				),
				PostbackAction(
					label='WITA',
					text='Waktu Indonesia Tengah',
					data='/zona wita'
				),
				PostbackAction(
					label='WIT',
					text='Waktu Indonesia Timur',
					data='/zona wit'
				)
			]
		)
	)
	return pilih

def pengaturan(args):
	try:
		
		data = db.child("pengguna").get().val()[args]
		try:
			tambahan = data["tambahan"]
			try:
				lokasi = tambahan["lokasi"]["nama_lokasi"]
			except:
				lokasi = "Tidak diketahui"
			try:
				lahir = tambahan["tanggal_lahir"]
				utahun, ubulan, utanggal = lahir.split('-')
				
				sekarang = datetime.utcfromtimestamp(time.time())
				tanggal = int(sekarang.strftime('%d'))
				dbulan = int(sekarang.strftime('%m'))
				tahun = int(sekarang.strftime('%Y'))
				umur = tahun - int(utahun)
					
				if tanggal < int(utanggal):
					if dbulan < int(ubulan):
						umur = umur - 1
				umur = str(umur)+" tahun"
			except:
				umur = "Tidak diketahui"
		except:
			lokasi = "Tidak diketahui"
			umur = "Tidak diketahui"

		member 	= data["waktu_add"]
		gambar 	= data["foto"]
		nama 	= data["nama"]
		total_seconds = time.time() - member

		MINUTE  = 60
		HOUR	= MINUTE * 60
		DAY	 = HOUR * 24
		MONTH = DAY * 30
		YEAR = MONTH * 12

		years 	= int( total_seconds / YEAR )
		months 	= int( (total_seconds % YEAR) / MONTH )
		days	= int( ( total_seconds % MONTH ) / DAY )
		hours	= int( ( total_seconds % DAY ) / HOUR )
		minutes	= int( ( total_seconds % HOUR ) / MINUTE )
		seconds	= int( total_seconds % MINUTE )

		string = list()
		if years > 0:
			string.append(str(years) + " tahun")
		if months > 0:
			string.append(str(months) + " bulan")
		if days > 0:
			string.append(str(days) + " hari")
		if hours > 0:
			string.append(str(hours) + " jam")
		if minutes > 0:
			string.append(str(minutes) + " menit")
		if seconds > 0:
			string.append(str(seconds) + " detik")
		else:
			if len(string) == 0:string.append("0 detik")

		tanggal = datetime.utcfromtimestamp(member)
		member = tanggal.strftime('Member sejak %d '+bulan(int(tanggal.strftime('%m')))+' %Y')
		sekarang = datetime.utcfromtimestamp(time.time())
		minimum = str(int(sekarang.strftime('%Y')) - 60)
		maksimum = str(int(sekarang.strftime('%Y')) - 13)
		initial = str(int(sekarang.strftime('%Y')) - 19)
		durasi = "("+string[0]+" yang lalu)"

		pesan = BubbleContainer(
			header=BoxComponent(
				layout='vertical',
				contents=[
					TextComponent(
						text='Pengaturan',
						align='start',
						weight='bold',
						color='#a2a2a2'
					)
				]
			),
			hero=ImageComponent(
				url=gambar,
				size='full',
				aspect_ratio='1:1',
				aspect_mode='cover'
			),
			body=BoxComponent(
				layout='vertical',
				contents=[
					TextComponent(
						text=nama,
						size='lg',
						align='center',
						weight='bold'
					),
					BoxComponent(
						layout='horizontal',
						margin='md',
						contents=[
							BoxComponent(
								layout='baseline',
								contents=[
									IconComponent(
										url='https://mbtskoudsalg.com/images/location-clipart-map-icon-3.jpg',
										size='xxs'
									),
									TextComponent(
										text=lokasi,
										margin='sm',
										size='xs',
										color='#8f8f8f'
									)
								]
							)
						]
					),
					BoxComponent(
						layout='baseline',
						margin='sm',
						contents=[
							TextComponent(
								text='Umur',
								flex=1,
								size='xxs',
								color='#737373'
							),
							TextComponent(
								text=umur,
								flex=4,
								size='xxs',
								align='start',
								color='#737373'
							)
						]
					),
					TextComponent(
						text=member,
						flex=1,
						size='xxs',
						color='#737373',
						wrap=True
					),
					TextComponent(
						text=durasi,
						size='xxs',
						align='start',
						color='#737373'
					)
				]
			),
			footer=BoxComponent(
				layout='vertical',
				contents=[
					ButtonComponent(
						action=PostbackAction(
							label='Ubah panggilan',
							text='Ubah nama panggilan',
							data='/nick '+args
						)
					),
					ButtonComponent(
						action=PostbackAction(
							label='Ubah zona waktu',
							text='Ubah zona waktu',
							data='/zona_waktu'
						)
					),
					ButtonComponent(
						action=PostbackAction(
							label='Ubah lokasi',
							text='Ubah lokasi',
							data='/lokasi'
						)
					),
					ButtonComponent(
						action=DatetimePickerAction(
							label='Ubah tanggal lahir',
							data='/tanggal_lahir '+args,
							mode='date',
							max=maksimum+'-12-31',
							min=minimum+'-01-01',
							initial=initial+'-01-01'
						)
					),
					ButtonComponent(
						action=PostbackAction(
							label='Sosial Media',
							text='Tambah sosial media',
							data='/sosmed '+args
						)
					)
				]
			)
		)
		kirim = FlexSendMessage(
			alt_text='Pengaturan',
			contents=pesan
		)
		return kirim
	except Exception as e:
		try:
			et, ev, tb = sys.exc_info()
			lineno = tb.tb_lineno
			fn = tb.tb_frame.f_code.co_filename
			return TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
		except:
			return TextSendMessage(text="Undescribeable error detected!!")

def download_film(args):
	result = list()
	try:
		url = urllib.request.urlopen(urllib.request.Request('https://yts.am/api/v2/list_movies.json?query_term='+urllib.parse.quote(args), headers={'User-Agent': "Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)"}))
		udict = url.read().decode('utf-8')
		data = json.loads(udict)["data"]["movies"]
		for film in data:
			judul = film["title_long"]
			rating = film["rating"]
			durasi = film["runtime"]
			genres = ", ".join(film["genres"])
			bahasa = film["language"]
			trailer = "https://youtube.com/watch?v="+film["yt_trailer_code"]
			download = film["torrents"]
			gambar = urllib.parse.quote(film["medium_cover_image"]).replace('%5C','').replace("%3A",":")
			gambar = "https://ytss.unblocked.lol"+gambar[14:]
			tombol = list()
			for s in download:
				tombol.append(
					ButtonComponent(
						action=URIAction(
							label=s["quality"],
							uri=s["url"]
						),
						color='#cf4d6a',
						style='primary'
					)
				)
			bintang = list()
			n = 2
			while n <= rating:
				bintang.append(
					IconComponent(
						url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'
						)
					)
				n = n + 2
			if len(bintang) < 5:
				sisa_bintang = 5 - len(bintang)
				n = 0
				while n < sisa_bintang:
					bintang.append(
						IconComponent(
							url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png'
						)
					)
					n = n + 1
			bintang.append(
				TextComponent(
					text=str(rating),
					flex=0,
					margin='md',
					size='sm',
					color='#999999'
				)
			)
			result.append(
				BubbleContainer(
					hero=ImageComponent(
						url=gambar,
						size='full',
						aspect_mode='cover',
						aspect_ratio='3:4'
					),
					body=BoxComponent(
						layout='vertical',
						contents=[
							TextComponent(
								text=judul,
								size='xl',
								align='center',
								weight='bold',
								wrap=True
							),
							BoxComponent(
								layout='baseline',
								margin='md',
							contents=bintang
							),
							BoxComponent(
								layout='vertical',
								margin='lg',
								contents=[
									BoxComponent(
										layout='baseline',
										contents=[
											TextComponent(
												text='Durasi',
												flex=1,
												size='sm',
												color='#aaaaaa'
											),
											TextComponent(
												text=str(durasi),
												flex=3,
												size='sm',
												color='#666666',
												wrap=True
											)
										]
									),
									BoxComponent(
										layout='baseline',
										contents=[
											TextComponent(
												text='Genres',
												flex=1,
												size='sm',
												color='#aaaaaa'
											),
											TextComponent(
												text=genres,
												flex=3,
												size='sm',
												color='#666666',
												wrap=True
											)
										]
									),
									BoxComponent(
										layout='baseline',
										contents=[
											TextComponent(
												text='Bahasa',
												flex=1,
												size='sm',
												color='#aaaaaa'
											),
											TextComponent(
												text=bahasa,
												flex=3,
												size='sm',
												color='#666666',
												wrap=True
											)
										]
									)
								]
							),
							ButtonComponent(
								action=URIAction(
									label='Lihat Trailer',
									uri=trailer
								),
								color='#ae3737',
								margin='lg',
								style='primary'
							)
						]
					),
					footer=BoxComponent(
						layout='horizontal',
						spacing='sm',
						contents=tombol[:3]
					)
				)
			)
	except Exception as e:
		try:
			et, ev, tb = sys.exc_info()
			lineno = tb.tb_lineno
			fn = tb.tb_frame.f_code.co_filename
			result.append("[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
		except:
			result.append("Undescribeable error detected!!")

	return result

def gis(args):
	search = args.split()
	url = urllib.request.urlopen('https://www.googleapis.com/customsearch/v1?q='+'+'.join(search)+'&cx=012011408610071646553%3A9m9ecisn3oe&imgColorType=color&num=10&safe=off&searchType=image&key='+google_key)
	udict = url.read().decode('utf-8')
	data = json.loads(udict)
	result = list()
	for d in data["items"]:
		gambar = d["link"]
		if "http://" in gambar:
			imgur = os.popen("curl --request POST \
						--url https://api.imgur.com/3/image \
						--header 'Authorization: Client-ID 802f673008792da' \
						--form 'image="+gambar+"'").read()
			ganti = json.loads(imgur)
			gambar = ganti["data"]["link"]
		jenis = d["mime"].replace("image/","")
		tinggi = d["image"]["height"]
		lebar = d["image"]["width"]
		judul = d["title"]
		link = d["image"]["contextLink"]
		#balas("Here's your result for: "+args)
		#img(gambar)
		result.append(
			CarouselColumn(
				thumbnail_image_url=gambar,
				title=judul[:39],
				text='Size: '+str(lebar)+'x'+str(tinggi)+'\nType: '+jenis,
				actions=[
					URIAction(
						label='Sumber Gambar',
						uri=link
					)
				]
			)
		)
	hasil = TemplateSendMessage(
		alt_text="Hasil pencarian: "+args,
		template=CarouselTemplate(
			columns=result
		)
	)
	return hasil

def download(gambar, args):
	try:
		video = pafy.new(args)
		judul = video.title
		result = list()
		for s in video.streams:
			resolusi = s.resolution
			ekstensi = s.extension
			link = s.url
			ukuran = ukuran_file(int(s.get_filesize()))
			ukuran = str(ukuran[0])[:4]+" "+ukuran[1]
			result.append(
				BubbleContainer(
					hero=ImageComponent(
						url=gambar,
						size='full',
						aspect_ratio='1.51:1',
						aspect_mode='cover'
					),
					body=BoxComponent(
						layout='vertical',
						contents=[
							TextComponent(
								text=judul,
								size='md',
								align='start',
								weight='bold',
								wrap=True
							),
							BoxComponent(
								layout='baseline',
								margin='md',
								contents=[
									TextComponent(
										text='Resolusi',
										flex=2,
										size='sm',
										weight='bold'
									),
									TextComponent(
										text=resolusi,
										flex=2,
										size='sm'
									)
								]
							),
							BoxComponent(
								layout='baseline',
								contents=[
									TextComponent(
										text='Ukuran',
										flex=2,
										size='sm',
										weight='bold'
									),
									TextComponent(
										text=ukuran,
										flex=2,
										size='sm'
									)
								]
							)
						]
					),
					footer=BoxComponent(
						layout='horizontal',
						contents=[
							ButtonComponent(
								action=URIAction(
									label=ekstensi,
									uri=link
								),
								color='#008d86',
								style='primary'
							)
						]
					)
				)
			)
		pesan = FlexSendMessage(
			alt_text="Download "+judul,
			contents=CarouselContainer(
				contents=result
			)	
		)
		return pesan
	except Exception as e:
		try:
			et, ev, tb = sys.exc_info()
			lineno = tb.tb_lineno
			fn = tb.tb_frame.f_code.co_filename
			return TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
		except:
			return TextSendMessage(text="Undescribeable error detected!!")

def search_movie_imdb(film):
	ia = IMDb()
	movies = ia.search_movie(film)
	movie_ids = [i.movieID for i in movies]
	kumpulin = list()
	for ids in movie_ids:
		movie = ia.get_movie(ids)
		genres = ", ".join(movie['genres'])
		gambar = movie.get_fullsizeURL()
		bahasa = movie.guessLanguage()
		judul = movie['title']+' ('+str(movie['year'])+')'
		try:
			rating = movie['rating']
		except:
			rating = 0
		kumpulin.append(
			BubbleContainer(
				hero=ImageComponent(
					url=gambar,
					size='full',
					aspect_ratio='9:16',
					aspect_mode='cover'
				),
				body=BoxComponent(
					layout='vertical',
					contents=[
						TextComponent(
							text=judul,
							size='lg',
							align='start',
							weight='bold'
						),
						BoxComponent(
							layout='baseline',
							spacing='md',
							contents=[
								IconComponent(
									url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'
								),
								TextComponent(
									text=str(rating),
									size='md'
								)
							]
						),
						BoxComponent(
							layout='baseline',
							contents=[
								TextComponent(
									text='Bahasa',
									flex=1,
									size='xs',
									align='start'
								),
								TextComponent(
									text=bahasa,
									flex=3,
									size='xs',
									align='start'
								)
							]
						),
						BoxComponent(
							layout='baseline',
							contents=[
								TextComponent(
									text='Genres',
									size='xs'
								),
								TextComponent(
									text=genres,
									flex=3,
									size='xs',
									wrap=True
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
								label='Lihat Selengkapnya',
								text='Lihat info film '+judul+' dong..',
								data='/imdb '+str(ids)
							),
							color='#ffffff',
							height='sm'
						)
					]
				),
				styles=BubbleStyle(
					footer=BlockStyle(
						background_color='#0697bc'
					)
				)
			)
		)
	return kumpulin

def mau_nonton():
	pesan = FlexSendMessage(
				alt_text='MENU FILM',
				contents=
						CarouselContainer(
							contents=[
								BubbleContainer(
									hero=ImageComponent(
										url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_3_movie.png',
										size='full',
										aspect_ratio='20:13',
										aspect_mode='cover'
									),
									body=BoxComponent(
										layout='vertical',
										spacing='md',
										contents=[
											TextComponent(
												text='Now Playing',
												size='xl',
												align='center',
												gravity='center',
												weight='bold',
												color='#000000',
												wrap=True
											),
											TextComponent(
												text='Cek Film di XXI',
												align='center'
											),
											BoxComponent(
												layout='baseline',
												spacing='sm',
												margin='xl',
												contents=[
													TextComponent(
														text='Fungsi',
														flex=1,
														size='xs',
														align='start',
														weight='bold'
													),
													TextComponent(
														text='Cek film di bioskop kesayangan kamu',
														flex=4,
														size='xs',
														align='start',
														wrap=True
													)
												]
											)
										]
									), 
									footer=BoxComponent(
										layout='horizontal',
										margin='md',
										contents=[
											ButtonComponent(
												style='primary',
												color='#840000',
												action=MessageAction(
													label='Pilih',
													text='Cek film bioskop'
												)
											)
										]
									)
								),
								BubbleContainer(
									hero=ImageComponent(
										url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_3_movie.png',
										size='full',
										aspect_ratio='20:13',
										aspect_mode='cover'
									),
									body=BoxComponent(
										layout='vertical',
										spacing='md',
										contents=[
											TextComponent(
												text='IMDB',
												size='xl',
												align='center',
												gravity='center',
												weight='bold',
												color='#000000',
												wrap=True
											),
											TextComponent(
												text='Cari info film menarik?',
												align='center'
											),
											BoxComponent(
												layout='baseline',
												spacing='sm',
												margin='xl',
												contents=[
													TextComponent(
														text='Fungsi',
														flex=1,
														size='xs',
														align='start',
														weight='bold'
													),
													TextComponent(
														text='Mencari dan menampilkan info film',
														flex=4,
														size='xs',
														align='start',
														wrap=True
													)
												]
											)
										]
									), 
									footer=BoxComponent(
										layout='horizontal',
										margin='md',
										contents=[
											ButtonComponent(
												style='primary',
												color='#840000',
												action=MessageAction(
													label='Pilih',
													text='Cek film dong'
												)
											)
										]
									)
								),
								BubbleContainer(
									hero=ImageComponent(
										url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_3_movie.png',
										size='full',
										aspect_ratio='20:13',
										aspect_mode='cover'
									),
									body=BoxComponent(
										layout='vertical',
										spacing='md',
										contents=[
											TextComponent(
												text='Download Film',
												size='xl',
												align='center',
												gravity='center',
												weight='bold',
												color='#000000',
												wrap=True
											),
											TextComponent(
												text='Gamau ke bioskop?\nDownload aja',
												wrap=True,
												align='center'
											),
											BoxComponent(
												layout='baseline',
												spacing='sm',
												margin='xl',
												contents=[
													TextComponent(
														text='Fungsi',
														flex=1,
														size='xs',
														align='start',
														weight='bold'
													),
													TextComponent(
														text='Download film',
														flex=4,
														size='xs',
														align='start',
														wrap=True
													)
												]
											),
											BoxComponent(
												layout='baseline',
												spacing='sm',
												margin='xl',
												contents=[
													TextComponent(
														text='Note',
														flex=1,
														size='xs',
														align='start',
														weight='bold',
													),
													TextComponent(
														text='Harus punya torrent downloader untuk mendownload film',
														flex=4,
														size='xs',
														align='start',
														wrap=True
													)
												]
											)
										]
									), 
									footer=BoxComponent(
										layout='horizontal',
										margin='md',
										contents=[
											ButtonComponent(
												style='primary',
												color='#840000',
												action=MessageAction(
													label='Pilih',
													text='Mau download film'
												)
											)
										]
									)
								)
							]
						)
					)
	return pesan

def youtube(args):
	try:
		if "<" in args or ">" in args:
			args = args.replace("<","").replace(">","")
		search = args.split()
		url = urllib.request.urlopen('https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&order=relevance&q='+'+'.join(search)+'&type=video&key='+google_key)
		udict = url.read().decode('utf-8')
		data = json.loads(udict)
		result = list()
		num = 1
		for d in data["items"]:
			link 		= 'https://youtube.com/watch?v='+d["id"]["videoId"]
			judul 		= d["snippet"]["title"]
			channel 	= d["snippet"]["channelTitle"]
			thumbnails 	= d["snippet"]["thumbnails"]["high"]["url"]
			data 		= json.loads(urllib.request.urlopen('https://www.googleapis.com/youtube/v3/videos?id='+d["id"]["videoId"]+'&key=AIzaSyAsn3d5sxrVwgYzIPgLS4mrFoqepJR5RzE&part=snippet,contentDetails,statistics,status').read().decode('utf-8'))["items"][0]
			durasi 		= data["contentDetails"]["duration"]
			durasi 		= durasi.replace("PT","").replace("M"," menit, dan ").replace("S"," detik.")
			statistik 	= data["statistics"]
			
			try:
				penonton = statistik["viewCount"]
				if int(penonton) > 1000000000:
					akhiran = penonton[-9:]
					penonton = penonton.replace(akhiran," miliar")
				elif int(penonton) > 1000000:
					akhiran = penonton[-6:]
					penonton = penonton.replace(akhiran," juta")
				elif int(penonton) > 1000:
					akhiran = penonton[-3:]
					penonton = penonton.replace(akhiran," ribu")
			except:
				penonton = "Tidak ditampilkan"

			try:
				disukai = statistik["likeCount"]
				if int(disukai) > 1000000000:
					akhiran = disukai[-9:]
					disukai = disukai.replace(akhiran," miliar")
				elif int(disukai) > 1000000:
					akhiran = disukai[-6:]
					disukai = disukai.replace(akhiran," juta")
				elif int(disukai) > 1000:
					akhiran = disukai[-3:]
					disukai = disukai.replace(akhiran," ribu")
			except:
				disukai = "Tidak ditampilkan"

			try:
				tidak_disukai = statistik["dislikeCount"]
				if int(tidak_disukai) > 1000000000:
					akhiran = tidak_disukai[-9:]
					tidak_disukai = tidak_disukai.replace(akhiran," miliar")
				elif int(tidak_disukai) > 1000000:
					akhiran = tidak_disukai[-6:]
					tidak_disukai = tidak_disukai.replace(akhiran," juta")
				elif int(tidak_disukai) > 1000:
					akhiran = tidak_disukai[-3:]
					tidak_disukai = tidak_disukai.replace(akhiran," ribu")
			except:
				tidak_disukai = "Tidak ditampilkan"
			
			try:
				komentar = statistik["commentCount"]
				if int(komentar) > 1000000000:
					akhiran = komentar[-9:]
					komentar = komentar.replace(akhiran," miliar")
				elif int(komentar) > 1000000:
					akhiran = komentar[-6:]
					komentar = komentar.replace(akhiran," juta")
				elif int(komentar) > 1000:
					akhiran = komentar[-3:]
					komentar = komentar.replace(akhiran," ribu")
			except:
				komentar = "Tidak ditampilkan"
			
			result.append(
				BubbleContainer(
					styles=BubbleStyle(
						header=BlockStyle(
							background_color='#730000'
						)
					),
					header=BoxComponent(
						layout='vertical',
						contents=[
							TextComponent(
								text=args.capitalize(),
								size='md',
								align='center',
								color='#ffffff',
								wrap=True
							)
						]
					),
					hero=ImageComponent(
						url=thumbnails,
						size='full',
						aspect_ratio='20:13',
						aspect_mode='cover'
					),
					body=BoxComponent(
						layout='vertical',
						contents=[
							TextComponent(
								text=judul,
								align='start',
								weight='bold',
								wrap=True
							),	
							BoxComponent(
								layout='baseline',
								margin='md',
								contents=[
									TextComponent(
										text='Channel',
										flex=1,
										size='xs',
										weight='bold',
									),
									TextComponent(
										text=channel,
										flex=3,
										size='xs',
										align='start',
										wrap=True
									)
								]
							),
							BoxComponent(
								layout='baseline',
								margin='md',
								contents=[
									TextComponent(
										text='Durasi',
										flex=1,
										size='xs',
										weight='bold',
									),
									TextComponent(
										text=durasi,
										flex=3,
										size='xs',
										align='start',
										wrap=True
									)
								]
							),
							BoxComponent(
								layout='vertical',
								spacing='none',
								margin='md',
								contents=[
									BoxComponent(
										layout='baseline',
										spacing='xs',
										contents=[
											IconComponent(
												url='https://freeiconshop.com/wp-content/uploads/edd/like-flat.png',
												margin='md'
											),
											TextComponent(
												text=disukai,
												wrap=True,
												margin='md'
											),
											IconComponent(
												url='https://freeiconshop.com/wp-content/uploads/edd/eye-flat.png',
												margin='md'
											),
											TextComponent(
												text=penonton,
												wrap=True,
												margin='md'
											)
										]
									),
									BoxComponent(
										layout='baseline',
										spacing='xs',
										contents=[
											IconComponent(
												url='https://image.flaticon.com/icons/png/512/433/433374.png',
												margin='md'
											),
											TextComponent(
												text=tidak_disukai,
												wrap=True,
												margin='md'
											),
											IconComponent(
												url='https://freeiconshop.com/wp-content/uploads/edd/chat-flat.png',
												margin='md'
											),
											TextComponent(
												text=komentar,
												wrap=True,
												margin='md'
											)
										]
									)
								]
							)
						]	
					),
					footer=BoxComponent(
						layout='horizontal',
						spacing='md',
						contents=[
							ButtonComponent(
								action=URIAction(
									label='Nonton',
									uri=link
								),
								color='#0062a3',
								style='primary'
							),
							ButtonComponent(
								action=PostbackAction(
									label='Download',
									text='Download video yang ke-'+str(num)+' dong',
									data='/ytdownload '+thumbnails+' '+link
								),
								style='secondary'
							)
						]
					)
				)
			)
			num = num + 1
			#balas("I've found this for you:")
			#img(thumbnails)
			#message(judul+"\nLink: "+link+"\nCreated by: "+channel+"\nDeskripsi: "+deskripsi)
		return result
	except Exception as e:
		try:
			et, ev, tb = sys.exc_info()
			lineno = tb.tb_lineno
			fn = tb.tb_frame.f_code.co_filename
			return TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
		except:
			return TextSendMessage(text="Undescribeable error detected!!")

def stimey(total_seconds):
	MINUTE  = 60
	HOUR	= MINUTE * 60
	DAY	 = HOUR * 24

	days	= int( total_seconds / DAY )
	hours	= int( ( total_seconds % DAY ) / HOUR )
	minutes	= int( ( total_seconds % HOUR ) / MINUTE )
	seconds	= int( total_seconds % MINUTE )

	string = list()
	if days > 0:
		string.append(str(days) + " hari")
	if hours > 0:
		string.append(str(hours) + " jam")
	if minutes > 0:
		string.append(str(minutes) + " menit")
	if seconds > 0:
		string.append(str(seconds) + " detik")
	else:
		if len(string) == 0:string.append("0 detik")
	if len(string) > 1:
		return ", ".join(string[:-1])+", dan "+string[-1]
	else:
		return ", ".join(string)

def info_film(args):
	try:
		url = urllib.request.urlopen('https://mtix.21cineplex.com/gui.movie_details.php?sid=&movie_id='+args)
		udict = url.read().decode('utf-8').replace('\r','').replace('\n','')
		data = re.findall('<div class="main-content">(.*?)<div class="col-xs-8 col-sm-11 col-md-11" style="font-weight: bold">',udict, re.S)[0]
		rating = re.findall('<img src="(.*?)" width="50" height="50"/>', data, re.S)[0]
		rating = 'https://mtix.21cineplex.com/'+rating
		data = re.findall('<div class="col-xs-8 col-sm-11 col-md-11" style="font-weight: bold">(.*?)<hr class="hr_separator" /><div class="footer" style="background-color: #ffffff">',udict, re.S)[0]
		gambar = re.findall('<img src="(.*?)" class="img-responsive pull-left gap-left" style="width:99%; margin-right:10px; margin-bottom: 10px;"/>',data, re.S)[0]
		judul = re.findall('<div>(.*?)</div>',data, re.S)[0]
		genre = re.findall('<div>(.*?)</div>',data, re.S)[1]
		sinopsis = re.findall('<div>(.*?)</div>',data, re.S)[2]
		sinopsis = sinopsis.replace('<p id="description">','').replace('</p><span id="readMore" style="text-decoration: underline"></span>','').replace('<br />','\n')
		trailer = re.findall(' BUY TICKET </button></p>                                        <p><button onclick="location.href = (.*?);" class="btn icon-btn btn-success" style="margin-top: 10px; width:90%;" > TRAILER </button></p>',data, re.S)[0]
		trailer = trailer.replace("'","")
		writer = re.findall('<strong>Writer</strong>:</p>                            <p>(.*?)</p>',data, re.S)[0]
		producer = re.findall('<br /><p style="margin-bottom: 5px"><strong>Producer</strong>:</p>                            <p> (.*?)</p>',data, re.S)[0]
		director = re.findall('<p style="margin-bottom: 5px"><strong>Director</strong>:</p>                            <p>(.*?)</p>',data, re.S)[0]
		cast = re.findall('<p style="margin-bottom: 5px"><strong>Cast</strong>:</p>                            <p>(.*?)</p>',data, re.S)[0]
		distributor = re.findall('<p style="margin-bottom: 5px"><strong>Distributor</strong>:</p>                            <p>(.*?)</p>',data, re.S)[0]
		durasi = re.findall('<p><span class="glyphicon glyphicon-time" style="margin-bottom: 10px"></span> (.*?)</p>',data, re.S)[0]
		tipe = re.findall('<p><a class="btn btn-default btn-outline disabled" style="color: #005350; font-weight: bold;"> (.*?)</a></p>',data, re.S)[0]

		hasil = FlexSendMessage(
			alt_text="Info "+judul,
			contents=CarouselContainer(
				contents=[
					BubbleContainer(
						hero=ImageComponent(
							url=gambar,
							size='full',
							aspect_ratio='9:16',
							aspect_mode='cover'
						)
					),
					BubbleContainer(
						header=BoxComponent(
							layout='vertical',
							contents=[
								BoxComponent(
									layout='baseline',
									margin='none',
									contents=[
										TextComponent(
											text=judul,
											size='md',
											align='start',
											weight='bold',
											color='#ffffff',
											wrap=True
										),
										IconComponent(
											url=rating,
											size='xxl'
										)
									]
								)
							]
						),
						body=BoxComponent(
							layout='vertical',
							contents=[
								BoxComponent(
									layout='horizontal',
									spacing='md',
									contents=[
										BoxComponent(
											layout='vertical',
											margin='sm',
											contents=[
												SeparatorComponent(
													color='#61ad57'
												),
												BoxComponent(
													layout='horizontal',
													contents=[
														SeparatorComponent(
															color='#61ad57'
														),
														TextComponent(
															text=tipe,
															align='center',
															weight='bold',
															color='#61ad57'
														),
														SeparatorComponent(
															color='#61ad57'
														)
													]
												),
												SeparatorComponent(
													color='#61ad57'
												)
											]
										),
										BoxComponent(
											layout='vertical',
											contents=[
												SeparatorComponent(
													color='#61ad57'
												),
												BoxComponent(
													layout='horizontal',
													contents=[
														SeparatorComponent(
															color='#61ad57'
														),
														TextComponent(
															text=durasi,
															align='center',
															weight='bold',
															color='#61ad57'
														),
														SeparatorComponent(
															color='#61ad57'
														)
													]
												),
												SeparatorComponent(
													color='#61ad57'
												)
											]
										)
									]
								),
								BoxComponent(
									layout='vertical',
									spacing='none',
									margin='lg',
									contents=[
										BoxComponent(
											layout='baseline',
											contents=[
												TextComponent(
													text='Genre',
													flex=1,
													size='sm'
												),
												TextComponent(
													text=genre,
													flex=2,
													size='sm',
													wrap=True
												)
											]
										),
										BoxComponent(
											layout='baseline',
											contents=[
												TextComponent(
													text='Writer',
													flex=1,
													size='sm'
												),
												TextComponent(
													text=writer,
													flex=2,
													size='sm',
													wrap=True
												)
											]
										),
										BoxComponent(
											layout='baseline',
											contents=[
												TextComponent(
													text='Director',
													flex=1,
													size='sm'
												),
												TextComponent(
													text=director,
													flex=2,
													size='sm',
													wrap=True
												)
											]
										),
										BoxComponent(
											layout='baseline',
											contents=[
												TextComponent(
													text='Distributor',
													flex=1,
													size='sm'
												),
												TextComponent(
													text=distributor,
													flex=2,
													size='sm',
													wrap=True
												)
											]
										),
										BoxComponent(
											layout='baseline',
											contents=[
												TextComponent(
													text='Producer',
													flex=1,
													size='sm'
												),
												TextComponent(
													text=producer,
													flex=2,
													size='sm',
													wrap=True
												)
											]
										),
										BoxComponent(
											layout='baseline',
											contents=[
												TextComponent(
													text='Cast',
													flex=1,
													size='sm'
												),
												TextComponent(
													text=cast,
													flex=2,
													size='sm',
													wrap=True
												)
											]
										)
									]
								)
							]
						),
						styles=BubbleStyle(
							header=BlockStyle(
								background_color='#61ad57'
							)
						)
					),
					BubbleContainer(
						header=BoxComponent(
							layout='vertical',
							contents=[
								TextComponent(
									text='Sinopsis',
									size='lg',
									align='start',
									weight='bold',
									color='#ffffff'
								)
							]
						),
						body=BoxComponent(
							layout='vertical',
							contents=[
								TextComponent(
									text=sinopsis,
									align='start',
									size='xs',
									wrap=True
								)
							]
						),
						footer=BoxComponent(
							layout='horizontal',
							contents=[
								ButtonComponent(
									action=URIAction(
										label='Lihat Trailer',
										uri=trailer
									),
									color='#61ad57',
									style='primary'
								)
							]
						),
						styles=BubbleStyle(
							header=BlockStyle(
								background_color='#61ad57'
							),
							footer=BlockStyle(
								background_color='#61ad57'
							)
						)
					)
				]
			)
		)
		return hasil
	except Exception as e:
		try:
			et, ev, tb = sys.exc_info()
			lineno = tb.tb_lineno
			fn = tb.tb_frame.f_code.co_filename
			return TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
		except:
			return TextSendMessage(text="Undescribeable error detected!!")

def tayang(kode_bioskop):
	try:
		url = urllib.request.urlopen('https://mtix.21cineplex.com/gui.schedule.php?sid=&find_by=1&cinema_id='+kode_bioskop+'&movie_id=')
		udict = url.read().decode('utf-8').replace('\r','').replace('\n','')
		#data = re.findall('<li class="list-group-item" style="border-color: #FFFFFF; padding:0px">(.*?)</p>', udict, re.S)
		
		gambar = re.findall('<img src="(.*?)" border="0" width="125" class="img-responsive pull-left gap-left" style="margin-right:10px;"/>',udict, re.S)
		gambar = gambar[1:]
		
		judul = re.findall('<a >(.*?)</a>',udict, re.S)
		judul = judul[1:]

		tipe = re.findall('<br>                     <span class="btn btn-default btn-outline disabled" style="color: #005350;">(.*?)</span>',udict, re.S)
		tipe = tipe[1:]

		rating = re.findall('</span>                     <span class="btn btn-default btn-outline disabled" style="color: #005350;">(.*?)</span>',udict, re.S)
		rating = rating[1:]

		durasi = re.findall('<span class="glyphicon glyphicon-time"></span> (.*?)</div>',udict, re.S)
		durasi = durasi[2:]

		tanggal = re.findall('<div class="row">                            <div class="col-xs-7" style="text-align:left"><p class="p_date"><p class="p_date">(.*?)</p></div>',udict, re.S)
		bioskop = re.findall('<h4><span><strong>(.*?)</strong></span></h4>',udict, re.S)[0]

		harga = re.findall('</p></div><div class="col-xs-5" style="text-align:right"><span class="p_price">(.*?)</span></div><br><p class="p_time pull-left" style="margin: 10px">',udict, re.S)

		jamku = {}
		main = list()
		waktu = re.findall('<p class="p_time pull-left" style="margin: 10px">(.*?) </p><div class="clearfix"></div>',udict, re.S)
		num = 1
		for i in waktu:
			data = re.findall('<a class="btn btn-outline-primary div_schedule" style="border-color: #337ab7;font-size:14px; margin-left:3px; margin-top:15px" href="#" onClick="(.*?)">(.*?)</a>',i, re.S)
			data1 = re.findall('<a class="btn btn-default btn-outline disabled div_schedule" style="color: #FFFFFF; background-color: #737373;font-size:14px; margin-left:3px; margin-top:15px" >(.*?)</a>',i, re.S)
			puluh = 0
			for jam in data1:
				try:
					if (len(jamku[num]) - 7 == puluh):
						jamku[num].append(SeparatorComponent())
						puluh = puluh + 7
					jamku[num].append(
						TextComponent(
							text=jam,
							align='center',
							color='#A5A5A5',
							size='xs'
						)
					)
					jamku[num].append(SeparatorComponent())
				except:
					jamku.update({num:[]})
					jamku[num].append(SeparatorComponent())
					jamku[num].append(
						TextComponent(
							text=jam,
							align='center',
							color='#A5A5A5',
							size='xs'
						)
					)
					jamku[num].append(SeparatorComponent())
			for klik, jam in data:
				if tanggal[0] in klik:
					try:
						if (len(jamku[num]) - 7 == puluh):
							jamku[num].append(SeparatorComponent())
							puluh = puluh + 7
						jamku[num].append(
							TextComponent(
								text=jam,
								align='center',
								size='xs',
								action=PostbackAction(
									label='Ingetin',
									text='Ingetin jam '+jam+' buat nonton '+judul[num-1]+' di '+bioskop.capitalize(),
									data='/reminder '+jam+' '+judul[num-1].replace(" ","+")+' '+bioskop.capitalize().replace(" ","+")+' '+tanggal[num-1]
								)
							)
						)
						jamku[num].append(SeparatorComponent())
					except:
						jamku.update({num:[]})
						jamku[num].append(SeparatorComponent())
						jamku[num].append(
							TextComponent(
								text=jam,
								align='center',
								size='xs',
								action=PostbackAction(
									label='Ingetin',
									text='Ingetin jam '+jam+' buat nonton '+judul[num-1]+' di '+bioskop.capitalize(),
									data='/reminder '+jam+' '+judul[num-1].replace(" ","+")+' '+bioskop.capitalize().replace(" ","+")+' '+tanggal[num-1]
								)
							)
						)
						jamku[num].append(SeparatorComponent())
			num = len(jamku) + 1
		num = 1
		gabungin = zip(gambar, judul, tipe, rating, durasi, tanggal, harga)
		if gabungin:
			res = list()
			for y in gabungin:
				img, title, tpe, rate, lama, tgl, rupiah = y
				clock = list()
				if len(jamku[num]) < 7:
					clock.append(
						BoxComponent(
							layout='horizontal',
							margin='md',
							contents=jamku[num]
						)
					)
				else:
					jwaktu = len(jamku[num])
					batas = 7
					while batas < jwaktu:
						awal = batas - 7
						clock.append(
							BoxComponent(
								layout='horizontal',
								margin='md',
								contents=jamku[num][awal:batas]
							)
						)
						batas = batas + 7
					awal = batas - 7
					if awal < jwaktu:
						clock.append(
							BoxComponent(
								layout='horizontal',
								margin='md',
								contents=jamku[num][awal:]
							)
						)
				res.append(
					BubbleContainer(
						header=BoxComponent(
							layout='vertical',
							contents=[
								TextComponent(
									text=bioskop,
									align='center',
									weight='bold',
									color='#ffffff',
									wrap=True
								)
							]
						),
						hero=ImageComponent(
							url=img,
							size='full',
							aspect_ratio='3:4',
							aspect_mode='cover'
						),
						body=BoxComponent(
							layout='vertical',
							contents=[
								TextComponent(
									text=title,
									size='xl',
									align='center',
									weight='bold',
									wrap=True
								),
								SeparatorComponent(margin='md'),
								BoxComponent(
									layout='horizontal',
									margin='md',
									contents=[
										TextComponent(
											text=tpe,
											flex=1,
											align='center',
											gravity='center',
											weight='bold'
										),
										SeparatorComponent(margin='md'),
										TextComponent(
											text=rate,
											flex=1,
											align='center',
											gravity='center',
											weight='bold'
										)
									]
								),
								SeparatorComponent(margin='md'),
								BoxComponent(
									layout='horizontal',
									margin='lg',
									contents=[
										BoxComponent(
											layout='baseline',
											spacing='md',
											margin='xl',
											contents=[
												IconComponent(
													url='https://www.freeiconspng.com/uploads/clock-png-5.png',
													margin='sm',
													aspect_ratio='1:1'
												),
												TextComponent(
													text=lama,
													flex=2,
													margin='lg',
													align='start'
												)
											]
										),
										BoxComponent(
											layout='baseline',
											spacing='md',
											margin='md',
											contents=[
												IconComponent(
													url='https://cdn4.iconfinder.com/data/icons/small-n-flat/24/calendar-512.png',
													margin='sm',
													aspect_ratio='1:1'
												),
												TextComponent(
													text=tgl
												)
											]
										)
									]
								),
								SeparatorComponent(margin='md'),
								TextComponent(
									text=rupiah,
									margin='md',
									size='lg',
									align='center'
								),
								SeparatorComponent(margin='md'),
								BoxComponent(
									layout='vertical',
									margin='md',
									contents=clock
								)
							]
						),
						footer=BoxComponent(
							layout='horizontal',
							contents=[
								ButtonComponent(
									PostbackAction(
										label='Lihat Selengkapnya',
										data='/cek_film_bioskop '+img.replace('https://web3.21cineplex.com/movie-images/','').replace('.jpg',''),
										text='Detail film '+title+'?'
									),
									color='#6d0000',
									style='primary'
								)
							]
						),
						styles=BubbleStyle(
							header=BlockStyle(
								background_color='#000000'
							),
							footer=BlockStyle(
								background_color='#000000'
							)
						)
					)
				)
				num = num + 1
			hasil = FlexSendMessage(
				alt_text="Sekarang main di "+bioskop,
				contents=CarouselContainer(
					contents=res
				)	
			)
			return hasil
	except Exception as e:
		try:
			et, ev, tb = sys.exc_info()
			lineno = tb.tb_lineno
			fn = tb.tb_frame.f_code.co_filename
			return TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
		except:
			return TextSendMessage(text="Undescribeable error detected!!")
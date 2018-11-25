import os
import re
import sys
import random
import time
import json

from acc import (line_bot_api, qz, handler, owner, namaBot)
from sesuatu import (panggil, film_quiz, pemain, hasil_akhir, skor_akhir)
from datetime import datetime
from threading import Timer
from linebot.models import *

soal = {}
playah = {}
kebenaran = {}
selesai = {}
aturan = ["Akan diberikan 10 soal yang harus dijawab dengan durasi kurang dari 1 menit.","Minimal ada 5 pemain dalam 1 grup","Pemain yang pertama kali menjawab benar akan diberikan 5 poin.","Pemain yang menjawab benar diurutan kedua akan diberikan 3 poin.","Pemain yang menjawab benar diurutan ketiga akan diberikan 1 poin.","Pemain yang menjawab benar tetapi mendapatkan urutan diatas 3 tidak mendapatkan poin.","Pemain yang menjawab salah akan dikurangi 1 poin.","Pemain yang menyerah tidak akan mendapat ataupun mengurangi poin, tetapi tidak dapat melanjutkan ke soal selanjutnya.","Pemain yang tidak menjawab akan dianggap menyerah dan tidak mengikuti soal berikutnya."]

def cek_pemain(ruangan):
	if ruangan in playah:
		jumlah_pemain = len(playah[ruangan]["pemain"])
		if jumlah_pemain < 5:
			line_bot_api.push_message(ruangan, TextSendMessage(text='Jumlah pemain kurang, permainan dibatalkan :('))
			del playah[ruangan]

def waktu_main(nomor_soal, ruangan):
	nomor, tanya, waktu = soal[ruangan]
	if nomor == nomor_soal:
		for pion in playah[ruangan]["pemain"]:
			if not (pion in kebenaran[ruangan]["benar"]) and not (pion in kebenaran[ruangan]["salah"]):
				kebenaran[ruangan]["nyerah"].append(pion)
		if len(kebenaran[ruangan]["nyerah"]) > 0:
			line_bot_api.push_message(ruangan, TextSendMessage(text='Kak '+", ".join([panggil(sender) for sender in kebenaran[ruangan]["nyerah"]])+' menyerah dan tidak dapat mengikuti permainan lagi :('))

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

			elif cmd == 'nyerah':
				if kirim in playah:
					if sender in playah[kirim]["pemain"]:
						if sender in kebenaran[kirim]["nyerah"]:return
						if playah[kirim]["status"] == "mulai":
							kebenaran[kirim]["nyerah"].append(sender)
							line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(sender)+' menyerah dan tidak dapat melanjutkan permainan :('))
				else:
					nomor, tanya, waktu = soal[kirim]
					data = qz.child("Quiz").child("Skor Pribadi").child(sender).get().val()
					nama = line_bot_api.get_profile(sender).display_name
					poin = data["poin"]
					try:
						gambar = line_bot_api.get_profile(sender).picture_url
					except:
						gambar = ""
					line_bot_api.reply_message(event.reply_token, hasil_akhir(nama, nomor-1, poin, gambar))
					del soal[kirim]
					del selesai[kirim]
	
			elif cmd == 'quiz':
				if args == 'ready':
					if event.source.type == 'user':
						try:
							data = qz.child("Quiz").child("Skor Pribadi").child(sender).get().val()
							poin = data["poin"]
						except:
							data = {"poin":0,"waktu":time.time()}
							qz.child("Quiz").child("Skor Pribadi").child(sender).set(data)
						pertanyaan = qz.child("Quiz").child("Pilihan").get().val()
						tanya = random.choice([i for i in pertanyaan])
						pilihan = [i for i in pertanyaan[tanya]["Jawaban"]]
						film = pertanyaan[tanya]["Film"]
						try:
							gambar = pertanyaan[tanya]["Gambar"]
						except:
							gambar = ""
						nomor = 1
						soal.update({kirim:[nomor, tanya, time.time()]})
						selesai.update({kirim:[]})
						selesai[kirim].append(tanya)
						line_bot_api.reply_message(event.reply_token, film_quiz("Pertanyaan "+str(nomor)+"/10", tanya, film, pilihan, gambar))
					else:
						line_bot_api.reply_message(event.reply_token, pemain(aturan))
						playah.update({kirim:{"status":"pending","pemain":[]}})
						t = Timer(60, cek_pemain, [kirim])
						t.start()
				else:
					line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kabarin kalau udah siap ya kak ;D'))
			
			elif cmd == 'join':
				durasi = time.time() - float(args)
				status = playah[kirim]["status"]
				if sender in playah[kirim]["pemain"]:
					line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(sender)+' sudah memasuki permainan ._.'))
					return
				if status == 'pending':
					if durasi < 30*60: #30 menit
						playah[kirim]["pemain"].append(sender)
						try:
							main = qz.child("Quiz").child("Skor").child(kirim).child(sender).get().val()
							poin = main["poin"]
						except:
							data = {"poin":0,"waktu":time.time()}
							qz.child("Quiz").child("Skor").child(kirim).child(sender).set(data)
						line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(sender)+' telah bergabung ;D'))
						if len(playah[kirim]["pemain"]) == 5:
							line_bot_api.push_message(kirim, [TextSendMessage(text='5 pemain telah terkumpul ;D'), TextSendMessage(text='Kalian bisa menunggu atau langsung memulai permainan'), TextSendMessage(text='Ketik /mulai jika ingin memulai permainan ;)')])
					else:
						line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Waktu untuk bergabung sudah habis kak '+panggil(sender)+' :('))
				else:
					line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(sender)+' tidak dapat bergabung karena permainan sedang berlangsung ;)'))

			elif cmd == 'jawab':
				if kirim in soal:
					nomor, tanya, waktu = soal[kirim]
					bertanya = qz.child("Quiz").child("Pilihan").get().val()
					bertanya = bertanya[tanya]
					try:
						menjawab = bertanya["Jawaban"][args]
					except:
						line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Tidak ada pilihan yang kak '+panggil(sender)+' pilih di soal ini :('))
						return
					if event.source.type == 'user':
						if menjawab == 'Benar':
							data = qz.child("Quiz").child("Skor Pribadi").child(sender).get().val()
							poin = data["poin"] + 1
							qz.child("Quiz").child("Skor Pribadi").child(sender).set({"poin":poin,"waktu":time.time()})
							pertanyaan = qz.child("Quiz").child("Pilihan").get().val()
							tanya = random.choice([i for i in pertanyaan])
							while tanya in selesai[kirim]:
								tanya = random.choice([i for i in pertanyaan])
							selesai[kirim].append(tanya)
							pilihan = [i for i in pertanyaan[tanya]["Jawaban"]]
							film = pertanyaan[tanya]["Film"]
							try:
								gambar = pertanyaan[tanya]["Gambar"]
							except:
								gambar = ""
							if nomor < 10:
								nomor = nomor + 1
								soal.update({kirim:[nomor, tanya, time.time()]})
								line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Kak '+panggil(sender)+' benar ;D'), film_quiz("Pertanyaan "+str(nomor)+"/10", tanya, film, pilihan, gambar)])
							else:
								data = qz.child("Quiz").child("Skor Pribadi").child(sender).get().val()
								nama = line_bot_api.get_profile(sender).display_name
								poin = data["poin"]
								gambar = line_bot_api.get_profile(sender).picture_url
								line_bot_api.reply_message(event.reply_token, hasil_akhir(nama, nomor, poin, gambar))
								del soal[kirim]
								del selesai[kirim]
						else:
							data = qz.child("Quiz").child("Skor Pribadi").child(sender).get().val()
							nama = line_bot_api.get_profile(sender).display_name
							poin = data["poin"]
							try:
								gambar = line_bot_api.get_profile(sender).picture_url
							except:
								gambar = ""
							line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Kak '+panggil(sender)+' salah :('), hasil_akhir(nama, nomor-1, poin, gambar)])
							del soal[kirim]
							del selesai[kirim]
					else:
						main = qz.child("Quiz").child("Skor").child(kirim).child(sender).get().val()
						try:
							poin = main["poin"]
						except:
							poin = 0
						if sender not in playah[kirim]["pemain"]:return
						benar = kebenaran[kirim]["benar"]
						salah = kebenaran[kirim]["salah"]
						nyerah = kebenaran[kirim]["nyerah"]
						if sender in benar or sender in salah or sender in nyerah:return
						if menjawab == 'Benar':
							if sender not in benar or sender not in salah or sender not in nyerah:
								if len(kebenaran[kirim]["benar"]) == 0:
									poin += 5
									kebenaran[kirim]["benar"].append(sender)
									line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(sender)+' benar dan mendapatkan 5 poin. Total: '+str(poin)+' poin ;D'))
								elif len(kebenaran[kirim]["benar"]) == 1:
									poin += 3
									kebenaran[kirim]["benar"].append(sender)
									line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(sender)+' benar dan mendapatkan 3 poin. Total: '+str(poin)+' poin ;D'))
								elif len(kebenaran[kirim]["benar"]) == 2:
									poin += 1
									kebenaran[kirim]["benar"].append(sender)
									line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(sender)+' benar dan mendapatkan 1 poin. Total: '+str(poin)+' poin ;D'))
								else:
									kebenaran[kirim]["benar"].append(sender)
									line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(sender)+' benar ;)'))
						else:
							if (sender not in kebenaran[kirim]["benar"]) or (sender not in kebenaran[kirim]["salah"]) or (sender not in kebenaran[kirim]["nyerah"]):
								poin = poin - 1
								kebenaran[kirim]["salah"].append(sender)
								line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(sender)+' salah, dikurangi 1 poin. :(\nTotal: '+str(poin)+' poin.'))
						
						if nomor < 10:
							benar = len(kebenaran[kirim]["benar"])
							salah = len(kebenaran[kirim]["salah"])
							nyerah = len(kebenaran[kirim]["nyerah"])
							if (benar + salah + nyerah) == len(playah[kirim]["pemain"]):
								pertanyaan = qz.child("Quiz").child("Pilihan").get().val()
								tanya = random.choice([i for i in pertanyaan])
								pilihan = [i for i in pertanyaan[tanya]["Jawaban"]]
								film = pertanyaan[tanya]["Film"]
								try:
									gambar = pertanyaan[tanya]["Gambar"]
								except:
									gambar = ""
								nomor = nomor + 1
								soal.update({kirim:[nomor, tanya, time.time()]})
								line_bot_api.push_message(kirim, film_quiz("Pertanyaan "+str(nomor)+"/10", tanya, film, pilihan, gambar))
								nyerah = [i for i in kebenaran[kirim]["nyerah"]]
								kebenaran.update({kirim:{"benar":[],"salah":[],"nyerah":nyerah}})
								t = Timer(60, waktu_main, (nomor, kirim))
								t.start()
						else:
							skornya = qz.child("Quiz").child("Skor").child(kirim).get().val()
							skor_trakhir = {}
							for u in skornya:
								total_skor = skornya[u]["poin"] + poin
								skor_trakhir.update({u:total_skor})
							line_bot_api.reply_message(event.reply_token, skor_akhir(skor_trakhir))
							del playah[kirim]
							del kebenaran[kirim]
						data = {"poin":poin,"waktu":time.time()}
						qz.child("Quiz").child("Skor").child(kirim).child(sender).set(data)
	
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

	if text == '/mulai':
		if kirim in playah:
			if playah[kirim]["status"] == 'pending':
				para_pemain = [i for i in playah[kirim]["pemain"]]
				playah[kirim].update({"status":"mulai","pemain":para_pemain})
				pertanyaan = qz.child("Quiz").child("Pilihan").get().val()
				tanya = random.choice([i for i in pertanyaan])
				pilihan = [i for i in pertanyaan[tanya]["Jawaban"]]
				film = pertanyaan[tanya]["Film"]
				try:
					gambar = pertanyaan[tanya]["Gambar"]
				except:
					gambar = ""
				nomor = 1
				kebenaran.update({kirim:{"benar":[],"salah":[],"nyerah":[]}})
				soal.update({kirim:[nomor, tanya, time.time()]})
				t = Timer(20, waktu_main, (nomor, kirim))
				t.start()
				line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Permainan dimulai ;)'), film_quiz("Pertanyaan "+str(nomor)+"/10", tanya, film, pilihan, gambar)])
			else:
				line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Permainan sudah dimulai ._.'))
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import requests, json


import errno
import os
import sys, random, datetime, time, re
import tempfile
import urllib
import cmds
import cinemaxxi
import yify_torrent
import acc
import imp
import firebase_admin

#from google.auth import app_engine
from firebase_admin import db
from firebase_admin import credentials
from acc import (namaBot, google_key, line_bot_api, handler)
from sesuatu import mau_nonton
from bs4 import BeautifulSoup
from linebot.exceptions import LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, CarouselContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, Error, ErrorDetail
)

app = Flask(__name__)

sleep = False

cred = credentials.Certificate('/Key/serviceAccountKey.json')
firebase_admin.initialize_app(cred, os.environ.get('DATABASE_URL'))

#===========[ NOTE SAVER ]=======================
notes = {}

kenalan = dict()
hobi = dict()
kumpul = dict()
pertanyaan = dict()

# Post Request
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text="Terima Kasih telah memasukkan "+namaBot.capitalize()+" dalam chat ini ;D\nJika kalian membutuhkan bantuanku, panggil saja :)",
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(
                            label=namaBot.capitalize(),
                            text=namaBot.capitalize()
                        )
                    )
                ]
            )
        )
    )

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(event.reply_token,
        [
            TextSendMessage(
                text='Terima kasih telah menambahkan '+namaBot+' sebagai teman ;D\n'+namaBot+' akan membantu kamu ketika kamu ingin bermain, cek film bioskop, download film, dan download youtube ;)\nKak '+line_bot_api.get_profile(event.source.user_id).display_name+' bisa mematikan notifikasi jika '+namaBot+' mengganggu :('
            ),
            TextSendMessage(
                text='Panggil saja namaku jika kamu ingin ditemani ;D',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(
                                label='Panggil',
                                text=namaBot.capitalize()
                            )
                        )
                    ]
                )
            )
        ]
    )
    data = db.reference('/')
    new_user = data.child('pengguna').set(
        {
            'user_id':event.source.user_id,
            'nama':line_bot_api.get_profile(event.source.user_id).display_name,
            'foto':line_bot_api.get_profile(event.source.user_id).picture_url,
            'status':line_bot_api.get_profile(event.source.user_id).status_message,
            'waktu_add':time.time()
        }
    )

@handler.add(PostbackEvent)
def handle_postback(event):
    cmds.handle_postback(event)
    yify_torrent.handle_postback(event)
    cinemaxxi.handle_postback(event)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    cinemaxxi.handle_location_message(event)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:

        ###################### OWNER ####################
        owner = 'U3fed832cbef28b87b7827b306506c8d5'

        startTime = time.time()
        cmds.handle_message(event)
        cinemaxxi.handle_message(event)
        yify_torrent.handle_message(event)

        text = event.message.text #simplify for receove message
        sender = event.source.user_id #get user_id
        gid = event.source.sender_id #get group_id
        profil = line_bot_api.get_profile(sender)
        nama = profil.display_name #Ini buat nama
        gambar = profil.picture_url #Ini profile picture
        status = profil.status_message #Ini status di line
        with open('pengguna.json','r') as f:
            try:
                pengguna = json.load(f)
            except:
                pengguna = {}

        def data_pengguna():
            return pengguna

        def stimey(total_seconds):
            try:

                MINUTE  = 60
                HOUR    = MINUTE * 60
                DAY     = HOUR * 24

                days    = int( total_seconds / DAY )
                hours   = int( ( total_seconds % DAY ) / HOUR )
                minutes = int( ( total_seconds % HOUR ) / MINUTE )
                seconds = int( total_seconds % MINUTE )

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

            except Exception as e:
                try:
                    et, ev, tb = sys.exc_info()
                    lineno = tb.tb_lineno
                    fn = tb.tb_frame.f_code.co_filename
                    return TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
                except:
                    return TextSendMessage(text="Undescribeable error detected!!")
        
        if isinstance(event.source, SourceGroup):
            kirim = gid
        elif isinstance(event.source, SourceRoom):
            kirim = event.source.room_id
        else:
            kirim = sender

        def test():
            pesan = FlexSendMessage(
                    alt_text='Test request granted',
                    contents=
                            CarouselContainer(
                                contents=[
                                    BubbleContainer(
                                        body=BoxComponent(
                                            layout='horizontal',
                                            contents=[
                                                TextComponent(
                                                    text='Lorem ipsum dolor sit amet',
                                                    wrap=True
                                                )
                                            ]
                                        ), 
                                        footer=BoxComponent(
                                            layout='horizontal',
                                            contents=[
                                                ButtonComponent(
                                                    style='primary',
                                                    action=URIAction(
                                                        label='Go',
                                                        uri='https://example.com'
                                                    )
                                                )
                                            ]
                                        )
                                    ),
                                    BubbleContainer(
                                        body=BoxComponent(
                                            layout='horizontal',
                                            contents=[
                                                TextComponent(
                                                    text='Hello world',
                                                    wrap=True
                                                )
                                            ]
                                        ),
                                        footer=BoxComponent(
                                            layout='horizontal',
                                            contents=[
                                                ButtonComponent(
                                                    style='primary',
                                                    action=URIAction(
                                                        label='Go',
                                                        uri='https://example.com'
                                                    )
                                                )
                                            ]   
                                        )
                                    )
                                ]
                            )
                    )
            return line_bot_api.push_message(kirim, pesan)

        def balas(args):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=args))

        def message(args):
            line_bot_api.push_message(kirim, TextSendMessage(text=args))

        def img(args):
            line_bot_api.push_message(kirim, ImageSendMessage(
                original_content_url=args,
                preview_image_url=args))

        if sender in pertanyaan:
            try:
                tau_hobi = list()
                info = list()
                bertanya, waktu = pertanyaan[sender]
                with open('pengguna.json','r') as f:
                    data = json.load(f)
                    for para in data['pengguna']:
                        if sender == para['user_id']:
                            info.append(para['nama'])
                            info.append(para['panggilan'])
                            info.append(para['tempat_lahir'])
                            info.append(para['tempat_tinggal'])
                            for hobby in para['hobi']:
                                tau_hobi.append(hobby)
                nama, panggilan, kelahiran, tinggal = info
                if text == "Namaku?":
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Kamu "+nama, quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="Nama", text="Namaku?")),QuickReplyButton(action=MessageAction(label="Panggilan", text="Nama panggilan?")),QuickReplyButton(action=MessageAction(label="Tempat Kelahiran", text="Dimana saya lahir?")),QuickReplyButton(action=MessageAction(label="Tempat Tinggal", text="Saya tinggal dimana?")),QuickReplyButton(action=MessageAction(label="Hobi", text="Hobiku?"))])))
                elif text == "Nama panggilan?":
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Setauku sih "+panggilan, quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="Nama", text="Namaku?")),QuickReplyButton(action=MessageAction(label="Panggilan", text="Nama panggilan?")),QuickReplyButton(action=MessageAction(label="Tempat Kelahiran", text="Dimana saya lahir?")),QuickReplyButton(action=MessageAction(label="Tempat Tinggal", text="Saya tinggal dimana?")),QuickReplyButton(action=MessageAction(label="Hobi", text="Hobiku?"))])))
                elif text == "Dimana saya lahir?":
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Kamu lahir di "+kelahiran, quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="Nama", text="Namaku?")),QuickReplyButton(action=MessageAction(label="Panggilan", text="Nama panggilan?")),QuickReplyButton(action=MessageAction(label="Tempat Kelahiran", text="Dimana saya lahir?")),QuickReplyButton(action=MessageAction(label="Tempat Tinggal", text="Saya tinggal dimana?")),QuickReplyButton(action=MessageAction(label="Hobi", text="Hobiku?"))])))
                elif text == "Saya tinggal dimana?":
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Di "+tinggal, quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="Nama", text="Namaku?")),QuickReplyButton(action=MessageAction(label="Panggilan", text="Nama panggilan?")),QuickReplyButton(action=MessageAction(label="Tempat Kelahiran", text="Dimana saya lahir?")),QuickReplyButton(action=MessageAction(label="Tempat Tinggal", text="Saya tinggal dimana?")),QuickReplyButton(action=MessageAction(label="Hobi", text="Hobiku?"))])))
                elif text == "Hobiku?":
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Hobi kamu ada "+str(len(tau_hobi))+" yaitu "+", ".join(tau_hobi), quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="Nama", text="Namaku?")),QuickReplyButton(action=MessageAction(label="Panggilan", text="Nama panggilan?")),QuickReplyButton(action=MessageAction(label="Tempat Kelahiran", text="Dimana saya lahir?")),QuickReplyButton(action=MessageAction(label="Tempat Tinggal", text="Saya tinggal dimana?")),QuickReplyButton(action=MessageAction(label="Hobi", text="Hobiku?"))])))
                else: del pertanyaan[sender]
            except Exception as e:
                try:
                    et, ev, tb = sys.exc_info()
                    lineno = tb.tb_lineno
                    fn = tb.tb_frame.f_code.co_filename
                    message("[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
                except:
                    message("Undescribeable error detected!!")

        if sender in kenalan and not text.lower() == namaBot:
            try:
                data = kenalan[sender]
                tanya, waktu = data[0], data[1]
                
                if tanya == "nama":
                    message("Kayaknya kalau manggil "+text+" kurang akrab :/")
                    time.sleep(1)
                    message("Jadi, kamu mau dipanggil apa?")
                    kenalan.update({sender:["panggilan",time.time()]})
                    kumpul.update({sender:[]})
                    kumpul[sender].append(text)

                elif tanya == "panggilan":
                    message("Okee, mulai sekarang kamu kupanggil "+text+" yak.")
                    time.sleep(1)
                    teks = TextSendMessage(text="Ohiya, hobi kamu apa?", quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="Dengar musik", text="Dengar musik")),QuickReplyButton(action=MessageAction(label="Programming", text="Programming")),QuickReplyButton(action=MessageAction(label="Nonton", text="Nonton")),QuickReplyButton(action=MessageAction(label="Membaca", text="Membaca")),QuickReplyButton(action=MessageAction(label="Olahraga", text="Olahraga")),QuickReplyButton(action=MessageAction(label="Kuliner", text="Kuliner")),QuickReplyButton(action=MessageAction(label="Traveling", text="Traveling")),QuickReplyButton(action=MessageAction(label="Hiking", text="Hiking")),QuickReplyButton(action=MessageAction(label="Menggambar", text="Menggambar")),QuickReplyButton(action=MessageAction(label="Melukis", text="Melukis")),QuickReplyButton(action=MessageAction(label="Menyanyi", text="Menyanyi"))]))
                    line_bot_api.push_message(kirim, teks)
                    kenalan.update({sender:["hobi",time.time()]})
                    hobi.update({sender:[]})
                    kumpul[sender].append(text)

                elif tanya == "hobi":
                    #rejection = ["tidak ada","gada","ga ada","gak ada","g ada","g punya","ga punya","gak punya","tidak punya"]
                    #for i in rejection:
                    #    if i in text.lower():
                    #        balas("Kok g punya?")
                    if ", " in text:
                        jawab = text.split(", ")
                    elif "," in text:
                        jawab = text.split(",")
                    else:
                        jawab = text
                    
                    try:
                        if "," in text:
                            for i in jawab:
                                hobi[sender].append(i)
                            if len(jawab) > 5:
                                balas("Lumayan banyak juga hobinya :O")
                        else:
                            hobi[sender].append(jawab)
                    except:
                        hobi[sender].append(jawab)
                    time.sleep(1)
                    message(kumpul[sender][1]+" tinggal dimana?")
                    kenalan.update({sender:["tempat_tinggal", time.time()]})

                elif tanya == "tempat_tinggal":
                    balas("Kurasa diriku masih perlu mengenal "+kumpul[sender][1]+" lebih lanjut :D")
                    time.sleep(1)
                    message("Kalau boleh tau, "+kumpul[sender][1]+" lahir dimana?")
                    kenalan.update({sender:["tempat_lahir", time.time()]})
                    kumpul[sender].append(text)

                elif tanya == "tempat_lahir":
                    balas("Okee terima kasih")
                    #kenalan.update({sender:["saudara",time.time()]})
                    kumpul[sender].append(text)
                    info = kumpul[sender]
                    hobby = hobi[sender]
                    del kenalan[sender]
                    pengguna["pengguna"] = []
                    pengguna["pengguna"].append({
                        "user_id":sender,
                        "nama":info[0],
                        "panggilan":info[1],
                        "hobi":hobby,
                        "tempat_tinggal":info[2],
                        "tempat_lahir":info[3]
                        })
                    del kumpul[sender]
                    #message(paste(pengguna["pengguna"]))
                    #PastebinAPI.paste(api_dev_key='002d3dfb7e78e5f051a0a2da91c5e1f6', api_paste_code=pengguna, api_user_key=paste_key(), paste_name='pengguna.json', paste_format=None, paste_private='unlisted', paste_expire_date=None)
                    with open('pengguna.json','w') as f:
                        json.dump(pengguna, f)
        
            except Exception as e:
                try:
                    et, ev, tb = sys.exc_info()
                    lineno = tb.tb_lineno
                    fn = tb.tb_frame.f_code.co_filename
                    message("[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
                except:
                    message("Undescribeable error detected!!")

        if text.lower() == namaBot:
            #balas_pesan = ["Iya ada apa"+nama+"?","Butuh bantuan?","Iya, kenapa?","Kenapa?","Iya "+nama, "Ada apa?",namaBot.capitalize()+" disini! ;D"]
            #text_message = TextSendMessage(text=random.choice(balas_pesan), quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="YouTube Search", text="YouTube")),QuickReplyButton(action=MessageAction(label="Google Image Search", text="Google Image")),QuickReplyButton(action=MessageAction(label="Ganteng?", text="Wahai Rion, apakah aku ganteng?")),QuickReplyButton(action=MessageAction(label="Cantik?", text="Wahai Rion, apakah aku cantik?"))]))
            pesan = FlexSendMessage(
                alt_text="Menu",
                contents=CarouselContainer(
                    contents=[
                        BubbleContainer(
                            styles=BubbleStyle(
                                header=BlockStyle(
                                    background_color='#223e7c'
                                )
                            ),
                            header=BoxComponent(
                                layout='vertical',
                                contents=[
                                    TextComponent(
                                        text='MENU',
                                        align='center',
                                        color='#ffffff'
                                    )
                                ]
                            ),
                            body=BoxComponent(
                                layout='vertical',
                                spacing='md',
                                contents=[
                                    BoxComponent(
                                        layout='horizontal',
                                        spacing='sm',
                                        contents=[
                                            BoxComponent(
                                                layout='vertical',
                                                spacing='sm',
                                                contents=[
                                                    ImageComponent(
                                                        url='https://i.postimg.cc/k4ybdVvm/movie-icon-11.png',
                                                        align='center',
                                                        action=MessageAction(
                                                            label='Film',
                                                            text='Nonton film kuy'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='Film',
                                                        size='xs',
                                                        align='center'
                                                    )
                                                ]
                                            ),
                                            BoxComponent(
                                                layout='vertical',
                                                spacing='sm',
                                                contents=[
                                                    ImageComponent(
                                                        url='https://goo.gl/Rtqc1r',
                                                        align='center',
                                                        action=MessageAction(
                                                            label='Drama',
                                                            text='Mau nonton drama nih'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='Drama',
                                                        size='xs',
                                                        align='center'
                                                    )
                                                ]
                                            ),
                                            BoxComponent(
                                                layout='vertical',
                                                spacing='sm',
                                                contents=[
                                                    ImageComponent(
                                                        url='https://goo.gl/S9GjL7',
                                                        align='center',
                                                        action=MessageAction(
                                                            label='YouTube',
                                                            text='Mau nonton YouTube'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='YouTube',
                                                        size='xs',
                                                        align='center'
                                                    )
                                                ]
                                            )
                                        ]
                                    ),
                                    BoxComponent(
                                        layout='horizontal',
                                        spacing='sm',
                                        contents=[
                                            BoxComponent(
                                                layout='vertical',
                                                spacing='sm',
                                                contents=[
                                                    ImageComponent(
                                                        url='https://i.postimg.cc/DzD04rPf/70.png',
                                                        align='center',
                                                        action=MessageAction(
                                                            label='Main',
                                                            text='Main yuk'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='Permainan',
                                                        size='xs',
                                                        align='center'
                                                    )
                                                ]
                                            ),
                                            BoxComponent(
                                                layout='vertical',
                                                spacing='sm',
                                                contents=[
                                                    ImageComponent(
                                                        url='https://i.postimg.cc/rpzzpnWY/01.png',
                                                        align='center',
                                                        action=MessageAction(
                                                            label='Lokasi',
                                                            text='Update Lokasi'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='Update Lokasi',
                                                        wrap=True,
                                                        size='xs',
                                                        align='center'
                                                    )
                                                ]
                                            ),
                                            BoxComponent(
                                                layout='vertical',
                                                spacing='sm',
                                                contents=[
                                                    ImageComponent(
                                                        url='https://i.postimg.cc/SsMs6ng6/09.png',
                                                        align='center',
                                                        action=MessageAction(
                                                            label='Tanggal Lahir',
                                                            text='Update tanggal lahir'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='Tanggal Lahir',
                                                        size='xs',
                                                        align='center',
                                                        wrap=True
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                            footer=BoxComponent(
                                layout='baseline',
                                contents=[
                                    TextComponent(
                                        text='© Yasri Ridho Pahlevi',
                                        size='xxs',
                                        align='start'
                                    ),
                                    TextComponent(
                                        text='2018',
                                        size='xxs',
                                        align='end'
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, [TextComponent(text="Kamu ingin apa hari ini?"), pesan])
            #line_bot_api.push_message(kirim, pesan)

        elif text == "Nonton film kuy":
            balas("Ini aku punya beberapa fungsi kalau kak "+nama+" mau nonton film ;)")
            line_bot_api.push_message(kirim, mau_nonton())

        elif namaBot in text.lower() and not text.lower() == namaBot and not sender in cmds.perintah:
            
            if "apa" in text.lower():
                if text.lower()[len(text)-1] == "?":
                    balas(random.choice(["Ya","Tidak","Terkadang","Mungkin","Coba tanya lagi","Entah","Hmm..."]))
                else:
                    balas("Situ bertanya?")
            
            elif "kenalan" in text.lower():
                info = list()
                tau_hobi = list()
                with open('pengguna.json','r') as f:
                    try:
                        data = json.load(f)
                    except:
                        data = {}
                    try:
                        for para in data['pengguna']:
                            if sender == para['user_id']:
                                info.append(para['nama'])
                                info.append(para['panggilan'])
                                info.append(para['tempat_lahir'])
                                info.append(para['tempat_tinggal'])
                                for hobby in para['hobi']:
                                    tau_hobi.append(hobby)
                    except:pass
                    if len(info) > 0:
                        line_bot_api.push_message(kirim, TextSendMessage(text="Kita kan udah kenalan",quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="Nama", text="Namaku?")),QuickReplyButton(action=MessageAction(label="Panggilan", text="Nama panggilan?")),QuickReplyButton(action=MessageAction(label="Tempat Kelahiran", text="Dimana saya lahir?")),QuickReplyButton(action=MessageAction(label="Tempat Tinggal", text="Saya tinggal dimana?")),QuickReplyButton(action=MessageAction(label="Hobi", text="Hobiku?"))])))
                        pertanyaan.update({sender:[text, time.time()]})
                        #time.sleep(1)
                        #message("Nama lengkap: "+info[0]+"\nNama Panggilan: "+info[1]+"\nTempat Lahir: "+info[2]+"\nTempat Tinggal: "+info[3]+"\nHobi: "+", ".join(tau_hobi))
                    else:
                        balas("Boleh")
                        time.sleep(1)
                        message("Namaku Rion, kamu?")
                        time.sleep(1)
                        message("Nama lengkap yak ;D")
                        kenalan.update({sender:["nama",time.time()]})

    #=====[ LEAVE GROUP OR ROOM ]==========
        elif 'get out' == text.lower() or 'bye' == text.lower():
            if sender != owner:
                balas("STFU!")
                return
            if isinstance(event.source, SourceGroup):
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='Good Bye Cruel World'))
                line_bot_api.leave_group(event.source.group_id)
            elif isinstance(event.source, SourceRoom):
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='Good Bye Cruel World'))
                line_bot_api.leave_room(event.source.room_id)
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="No!"))

        ################################################

        elif text.lower() == "who am i?":
            #message("You're "+nama)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="You're "+nama))
            line_bot_api.push_message(kirim, ImageSendMessage(
                original_content_url=gambar,
                preview_image_url=gambar
            ))

        elif text[0] == "=":
            data = text[1:].split(" ",1)
            if len(data) > 1:
                cmd, args = data[0].lower(), data[1]
            else:
                cmd, args = data[0].lower(), ""
            
            if cmd == "test":
                balas("Test Request Granted my Dear.")
                message("Here's a picture for you.")
                line_bot_api.push_message(kirim, ImageSendMessage(
                    original_content_url='https://i.pinimg.com/originals/0b/45/54/0b45541af3e8d77e23498c1bc8d552f6.jpg',
                    preview_image_url='https://i.pinimg.com/originals/0b/45/54/0b45541af3e8d77e23498c1bc8d552f6.jpg'
                ))

            elif cmd == "say":
                if args:
                    balas(args)
                else:
                    balas("What should I say?")

            elif cmd == "reload":
                imp.reload(cmds)
                balas("Reloaded.")

            elif cmd == "e":
                if sender != owner:
                    message('STFU!')
                    return
                try:
                    ret = eval(args)
                    if ret == None:
                        message("Done.")
                        return
                    message(str(ret))
                except Exception as e:
                    try:
                        et, ev, tb = sys.exc_info()
                        lineno = tb.tb_lineno
                        fn = tb.tb_frame.f_code.co_filename
                        message("[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
                    except:
                        message("Undescribeable error detected!!")

            elif cmd == "owner":
                pesan = TemplateSendMessage(
                    alt_text='Owner',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='LINE',
                                text='Chat me about this bot.',
                                actions=[
                                    URITemplateAction(
                                        label='Add Me',
                                        uri='https://line.me/ti/p/~freedom_for_all'
                                    )
                                ]
                            ),
                            CarouselColumn(
                                title='INSTAGRAM',
                                text='Feel free to follow ;)',
                                actions=[
                                    URITemplateAction(
                                        label='Go to my Instagram',
                                        uri='https://instagram.com/yasridho'
                                    )
                                ]
                            )

                        ]
                    )   
                )
                line_bot_api.reply_message(event.reply_token, pesan)
            

    #=====[ CAROUSEL MESSAGE ]==========
        elif text == '/carousel':
            message = TemplateSendMessage(
                alt_text='OTHER MENU',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            title='ADD ME',
                            text='Contact Noir',
                            actions=[
                                URITemplateAction(
                                    label='>TAP HERE<',
                                    uri='https://line.me/ti/p/~freedom_for_all'
                                )
                            ]   
                        ),
                        CarouselColumn(
                            title='Instagram',
                            text='FIND ME ON INSTAGRAM',
                            actions=[
                                URITemplateAction(
                                    label='>TAP HERE!<',
                                    uri='https://instagram.com/yasridho'
                                )
                            ]
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)
    #=====[ FLEX MESSAGE ]==========
        elif text == 'flex':
            bubble = BubbleContainer(
                direction='ltr',
                hero=ImageComponent(
                    url='https://i.pinimg.com/originals/0b/45/54/0b45541af3e8d77e23498c1bc8d552f6.jpg',
                    size='full',
                    aspect_ratio='20:13',
                    aspect_mode='cover',
                    action=URIAction(uri='http://line.me/ti/p/~freedom_for_all', label='label')
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        # title
                        TextComponent(text='Noir', weight='bold', size='xl'),
                        # review
                        BoxComponent(
                            layout='baseline',
                            margin='md',
                            contents=[
                                IconComponent(size='sm', url='https://example.com/gold_star.png'),
                                IconComponent(size='sm', url='https://example.com/grey_star.png'),
                                IconComponent(size='sm', url='https://example.com/gold_star.png'),
                                IconComponent(size='sm', url='https://example.com/gold_star.png'),
                                IconComponent(size='sm', url='https://example.com/grey_star.png'),
                                TextComponent(text='4.0', size='sm', color='#999999', margin='md',
                                            flex=0)
                            ]
                        ),
                        # info
                        BoxComponent(
                            layout='vertical',
                            margin='lg',
                            spacing='sm',
                            contents=[
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='Place',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=1
                                        ),
                                        TextComponent(
                                            text='Ujung Pandang, Indonesia',
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5
                                        )
                                    ],
                                ),
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='Time',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=1
                                        ),
                                        TextComponent(
                                            text="10:00 - 23:00",
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5,
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
                footer=BoxComponent(
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        # separator
                        SeparatorComponent(),
                        # websiteAction
                        ButtonComponent(
                            style='link',
                            height='sm',
                            action=URIAction(label='Noir', uri="https://line.me/ti/p/~freedom_for_all")
                        )
                    ]
                ),
            )
            message = FlexSendMessage(alt_text="Hi there!", contents=bubble)
            line_bot_api.reply_message(
                event.reply_token,
                message
            )
#=======================================================================================================================
    ############ ERROR HANDLING ############

    except LineBotApiError as e:
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

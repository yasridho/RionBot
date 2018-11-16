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

from acc import (namaBot, google_key, line_bot_api, handler, db)
from sesuatu import (mau_nonton, pengaturan, panggil)
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

#===========[ NOTE SAVER ]=======================
notes = {}

perintah = {}

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
    line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(
                text="Terima Kasih telah memasukkan "+namaBot.capitalize()+" dalam chat ini ;D\nJika kalian membutuhkan bantuanku, panggil saja :)"
            ),
            TextSendMessage(
                text='Agar dapat menggunakan fitur-fitur yang ada, harus add '+namaBot.capitalize()+' sebagai teman dulu yak ;D',
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
        ]
    )
    if isinstance(event.source, SourceGroup):
        ruang = event.source.sender_id
    elif isinstance(event.source, SourceRoom):
        ruang = event.source.room_id
    
    db.child(event.source.type).child(ruang).set(time.time())
    try:
        jumlah = db.child(event.source.type).get().val()["total"]
        db.child(event.source.type).child("total").update(jumlah+1)
    except:
        db.child(event.source.type).child("total").set(1)

@handler.add(LeaveEvent)
def handle_leave(event):
    if isinstance(event.source, SourceGroup):
        ruang = event.source.sender_id
    elif isinstance(event.source, SourceRoom):
        ruang = event.source.room_id

    db.child(event.source.type).child(ruang).remove()
    try:
        jumlah = db.child(event.source.type).get().val()["total"]
        db.child(event.source.type).child("total").update(jumlah-1)
    except:
        db.child(event.source.type).child("total").set(0)

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
    data = {'nama':line_bot_api.get_profile(event.source.user_id).display_name,
            'foto':line_bot_api.get_profile(event.source.user_id).picture_url,
            'status':line_bot_api.get_profile(event.source.user_id).status_message,
            'waktu_add':time.time()}
    db.child("pengguna").child(event.source.user_id).set(data)
    try:
        jumlah = db.child("pengguna").get().val()["total"]
        db.child("pengguna").child("total").update(jumlah+1)
    except:
        db.child("pengguna").child("total").set(1)

@handler.add(PostbackEvent)
def handle_postback(event):
    cmds.handle_postback(event)
    yify_torrent.handle_postback(event)
    cinemaxxi.handle_postback(event)
    sender = event.source.user_id
    if isinstance(event.source, SourceGroup):
        kirim = gid
    elif isinstance(event.source, SourceRoom):
        kirim = event.source.room_id
    else:
        kirim = sender
    
    try:
        if event.postback.data[0] == '/':
            data = event.postback.data[1:].split(" ",1)
            if len(data) > 1:
                cmd, args = data[0].lower(), data[1]
            else:
                cmd, args = data[0].lower(), ""

            if cmd == "pengaturan":
                line_bot_api.reply_message(event.reply_token, pengaturan(sender))

            elif cmd == "lokasi":
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Share lokasi dulu kak '+panggil(sender)+' ;)', quick_reply=QuickReply(items=[QuickReplyButton(action=LocationSendMessage(label='Share lokasi'))])))
                perintah.update({sender:['lokasi',time.time()]})

            elif cmd == "nick":

                if args == sender:
                    gunakan = args
                else:
                    gunakan = sender

                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Kak "+panggil(gunakan)+" mau dipanggil apa?"))
                perintah.update({sender:['panggilan', time.time()]})

            elif cmd == "tanggal_lahir":
                
                if args == sender:
                    gunakan = args
                else:
                    gunakan = sender
                    
                db.child("pengguna").child(gunakan).child("tambahan").child("tanggal_lahir").set(event.postback.params['date'])
                sekarang = datetime.datetime.utcfromtimestamp(time.time())
                tanggal = int(sekarang.strftime('%d'))
                bulan = int(sekarang.strftime('%m'))
                tahun = int(sekarang.strftime('%Y'))
                utahun, ubulan, utanggal = event.postback.params['date'].split('-')
                umur = tahun - int(utahun)
                    
                if tanggal < int(utanggal):
                    if bulan < int(ubulan):
                        umur = umur - 1

                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Kak "+panggil(gunakan)+" sekarang berumur "+str(umur)+" tahun ;D"))



    except Exception as e:
        try:
            et, ev, tb = sys.exc_info()
            lineno = tb.tb_lineno
            fn = tb.tb_frame.f_code.co_filename
            line_bot_api.push_message(kirim, TextSendMessage(text="[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e))))
        except:
            line_bot_api.push_message(kirim, TextSendMessage(text="Undescribeable error detected!!"))

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    cinemaxxi.handle_location_message(event)
    if event.source.user_id in perintah:
        komando, waktu = perintah[event.source.user_id]
        if komando == "lokasi":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Kak '+panggil(event.source.user_id)+' sekarang berada di '+event.message.address+' ;)'))
            data = {'nama_lokasi':event.message.address,
                    'latitude':event.message.latitude,
                    'longitude':event.message.longitude}
            db.child("pengguna").child(event.source.user_id).child("tambahan").child("lokasi").set(data)
            del perintah[event.source.user_id]


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
        nama = panggil(sender) #Ini buat nama
        gambar = profil.picture_url #Ini profile picture
        status = profil.status_message #Ini status di line

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

        if sender in perintah:
            komando, waktu = perintah[sender]

            if komando == "panggilan":
                if text == "Ubah nama panggilan":return
                db.child("pengguna").child(sender).child("tambahan").child("panggilan").set(text)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Mulai sekarang kakak akan kupanggil "+text+" ;D"))
                del perintah[sender]

        if text.lower() == namaBot:
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
                                                        action=PostbackAction(
                                                            label='Main',
                                                            text='Main kuy',
                                                            data='/main'
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
                                                        url='https://i.postimg.cc/q75v5Q3X/69.png',
                                                        align='center',
                                                        action=PostbackAction(
                                                            label='Pengingat',
                                                            text='Atur pengingat',
                                                            data='/pengingat'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='Pengingat',
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
                                                        url='https://i.postimg.cc/YqqXtBh6/settings-3-icon.png',
                                                        align='center',
                                                        action=PostbackAction(
                                                            label='Pengaturan',
                                                            text='Pengaturan',
                                                            data='/pengaturan'
                                                        )
                                                    ),
                                                    TextComponent(
                                                        text='Pengaturan',
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
                                        text='© YRP',
                                        size='xxs',
                                        align='start'
                                    ),
                                    TextComponent(
                                        text=namaBot.capitalize()+' '+os.environ.get('HEROKU_RELEASE_VERSION'),
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

        elif text == "Nonton film kuy":
            balas("Ini aku punya beberapa fungsi kalau kak "+nama+" mau nonton film ;)")
            line_bot_api.push_message(kirim, mau_nonton())

        elif namaBot in text.lower() and not text.lower() == namaBot and not sender in cmds.perintah:
            
            if "apa" in text.lower():
                if text.lower()[len(text)-1] == "?":
                    balas(random.choice(["Ya","Tidak","Terkadang","Mungkin","Coba tanya lagi","Entah","Hmm..."]))
                else:
                    balas("Situ bertanya?")

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

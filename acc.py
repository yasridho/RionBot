import os
from linebot import (LineBotApi, WebhookHandler)

namaBot = "rion"
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('SECRET_TOKEN'))
google_key = os.environ.get('GOOGLE_API_KEY')
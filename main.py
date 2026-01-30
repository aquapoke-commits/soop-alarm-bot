import discord
from discord.ext import tasks
import requests
import os
from flask import Flask
from threading import Thread

# --- 1. 가짜 웹사이트 설정 (Render가 봇을 죽이지 않게 함) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive! (Bot is running)"

def run():
    # Render는 기본적으로 10000번 포트 등을 사용하려 시도함
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. 봇 설정 ---
TOKEN = os.environ.get('DISCORD_TOKEN')
CHANNEL_ID = 1391612789918793810 # [수정필요] 본인의 채널 ID 숫자
BJ_ID = 'sksjr' # [수정필요] 대상 BJ 아이디

class SoopBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.is_online = False

    async def on_ready(self):
        print(f'{self.user} 봇 가동 시작!')
        self.check_stream.start()

    @tasks.loop(minutes=1)
    async def check_stream(self):
        url = f"https://bjapi.afreecatv.com/api/{BJ_ID}/station"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            res = requests.get(url, headers=headers)
            data = res.json()
            
            is_live = False
            if "broad" in data and data["broad"] is not None:
                is_live = True
            
            if is_live and not self.is_online:
                channel = self.get_channel(CHANNEL_ID)
                await channel.send(f"🚨 페가소스(sksjr)님이 방송을 켰습니다!\nhttps://bj.afreecatv.com/{BJ_ID}")
                self.is_online = True
            elif not is_live:
                self.is_online = False
                
        except Exception as e:
            print(f"에러: {e}")

# --- 3. 실행 ---
keep_alive() # 가짜 웹서버 먼저 실행
client = SoopBot()
client.run(TOKEN)


import discord
from discord.ext import tasks
import requests
import os
from flask import Flask
from threading import Thread

# --- 1. 가짜 웹사이트 설정 ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive! (Bot is running)"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. 봇 설정 (여러 명 관리 모드) ---
TOKEN = os.environ.get('DISCORD_TOKEN')
CHANNEL_ID = 1391612789918793810 # [수정필요] 본인의 실제 채널 ID

# [핵심 변경] 감시할 스트리머 목록 (아이디: 닉네임)
TARGET_STREAMERS = {
    'sksjr': 'DNS_Pegasos',
    'brake0': 'DNS_Braver',
    'dna0509': 'DNS_EnKoe',
    'lavishboy2': 'DNS_Reroll',
    'kdh3063': 'DNS_KAMDONG'
    # 여기에 계속 추가 가능: '아이디': '표시할이름',
}

class SoopBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        # 각 스트리머별로 방송 중인지 따로따로 기억해야 함 (초기값은 모두 False/방송안함)
        self.live_status = {bj_id: False for bj_id in TARGET_STREAMERS}

    async def on_ready(self):
        print(f'{self.user} 봇 가동 시작! 감시 대상: {len(TARGET_STREAMERS)}명')
        self.check_stream.start()

    @tasks.loop(minutes=1)
    async def check_stream(self):
        # 명단에 있는 스트리머를 한 명씩 차례대로 확인 (for문)
        for bj_id, nickname in TARGET_STREAMERS.items():
            url = f"https://bjapi.afreecatv.com/api/{bj_id}/station"
            headers = {"User-Agent": "Mozilla/5.0"}
            
            try:
                res = requests.get(url, headers=headers)
                data = res.json()
                
                is_now_live = False
                if "broad" in data and data["broad"] is not None:
                    is_now_live = True
                
                # 방송이 켜졌고(True), 봇이 기억하는 상태는 꺼짐(False)일 때 -> 알림 발송
                if is_now_live and not self.live_status[bj_id]:
                    channel = self.get_channel(CHANNEL_ID)
                    
                    # 닉네임을 활용해서 알림 메시지를 보냄
                    await channel.send(
                        f"🚨 **{nickname}**({bj_id})님이 방송을 켰습니다!\n"
                        f"보러가기: https://bj.afreecatv.com/{bj_id}"
                    )
                    
                    # 이 사람의 상태를 '방송 중'으로 변경
                    self.live_status[bj_id] = True
                    
                # 방송이 꺼져있다면 상태를 '방송 종료'로 변경
                elif not is_now_live:
                    self.live_status[bj_id] = False
                    
            except Exception as e:
                print(f"[{nickname}] 확인 중 에러 발생: {e}")

# --- 3. 실행 ---
keep_alive()
client = SoopBot()
client.run(TOKEN)



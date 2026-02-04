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

# --- 2. 봇 설정 ---
TOKEN = os.environ.get('DISCORD_TOKEN')
CHANNEL_ID = 1391612789918793810 # 작성자님 채널 ID

# 감시할 스트리머 목록
TARGET_STREAMERS = {
    'sksjr': 'DNS_Pegasos',
    'brake0': 'DNS_Braver',
    'dna0509': 'DNS_EnKoe',
    'lavishboy2': 'DNS_Reroll',
    'kdh3063': 'DNS_KAMDONG',
    'aquapoke': 'DNS_EeDuGi'
}

class SoopBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        # 각 스트리머별 방송 상태 기억 (초기값: False)
        self.live_status = {bj_id: False for bj_id in TARGET_STREAMERS}

    async def on_ready(self):
        print(f'{self.user} 봇 가동 시작! 감시 대상: {len(TARGET_STREAMERS)}명')
        self.check_stream.start()

    @tasks.loop(minutes=1)
    async def check_stream(self):
        # 명단에 있는 스트리머를 한 명씩 차례대로 확인
        for bj_id, nickname in TARGET_STREAMERS.items():
            url = f"https://bjapi.afreecatv.com/api/{bj_id}/station"
            headers = {"User-Agent": "Mozilla/5.0"}
            
            try:
                res = requests.get(url, headers=headers)
                data = res.json()
                
                is_now_live = False
                broad_no = None # 방송 번호 담을 변수

                # 방송 중인지 확인
                if "broad" in data and data["broad"] is not None:
                    is_now_live = True
                    # [핵심] 방송 고유 번호 추출 (직통 링크용)
                    broad_no = data["broad"]["broad_no"]
                
                # 방송이 켜졌고(True), 봇 기억은 꺼짐(False)일 때 -> 알림 발송
                if is_now_live and not self.live_status[bj_id]:
                    channel = self.get_channel(CHANNEL_ID)
                    
                    # [수정됨] 방송 번호를 포함한 직통 링크 생성
                    live_link = f"https://play.sooplive.co.kr/{bj_id}/{broad_no}"

                    await channel.send(
                        f"🚨 **{nickname}**({bj_id})님이 방송을 켰습니다!\n"
                        f"보러가기: {live_link}"
                    )
                    
                    # 상태를 '방송 중'으로 변경
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

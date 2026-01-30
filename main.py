import discord
from discord.ext import tasks
import requests
import os # 보안 설정을 위해 추가

# --- 설정 구간 (보안 적용) ---
# GitHub에 올릴 때는 토큰을 직접 적지 않고 os.environ을 씁니다.
TOKEN = os.environ.get('DISCORD_TOKEN') 
CHANNEL_ID = 123456789012345678 # 본인의 채널 ID (숫자)
BJ_ID = 'leesh2148' # 대상 BJ 아이디

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
            
            # 수정된 핵심 로직
            is_live = False
            if "broad" in data and data["broad"] is not None:
                is_live = True
            
            if is_live and not self.is_online:
                channel = self.get_channel(CHANNEL_ID)
                await channel.send(f"🚨 {BJ_ID}님이 방송을 켰습니다!\nhttps://bj.afreecatv.com/{BJ_ID}")
                self.is_online = True
            elif not is_live:
                self.is_online = False
                
        except Exception as e:
            print(f"에러: {e}")

client = SoopBot()
client.run(TOKEN)
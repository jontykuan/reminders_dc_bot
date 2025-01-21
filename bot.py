import discord
from discord.ext import commands
import json
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from config import LLMSTUDIO_BASE_URL, LLMSTUDIO_MODEL
import re

class WritingBot(commands.Bot):
    def __init__(self, port: int):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        self.prompts = self.load_prompts()
        self.scheduler = AsyncIOScheduler()
        self.llm = ChatOpenAI(
            base_url=LLMSTUDIO_BASE_URL,
            api_key="not-needed",
            model_name=LLMSTUDIO_MODEL,
            temperature=0.7
        )
        
        self.reminder_template = ChatPromptTemplate.from_messages([
            ("system", """你是一個可靠的寫作助手，你的名字是 {char_name}。以下是你的背景設定：{prompt}。
            請務必以第一人稱生成一個簡短的 (1-2 句) 提醒，語氣和個性需符合角色設定，不要使用表情符號。

            現在，你要對 {user_nickname} 說話，生成的內容是 {char_name} 催促 {user_nickname} 快點去寫作的提醒。

            輸出格式「絕對必須」是："{char_name}[符合角色的表情或動作]：[以第一人稱視角生成角色個性或設定對{user_nickname}的回應內容]"。

            錯誤範例：
            時間到囉，該開始寫作了！(缺少角色名字)
            *小精靈眨了眨眼* 時間到囉(格式不正確)

            正確範例：
            小精靈眨了眨眼：時間到囉，{user_nickname}，該開始寫作了！  # 明確使用 {user_nickname}
            惡魔露出邪惡的微笑：{user_nickname}，稿子呢？還不快寫？ # 明確使用 {user_nickname}
            """)
        ])

        self.setup_commands()
        
    def load_prompts(self):
        try:
            with open('prompts.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def save_prompts(self):
        with open('prompts.json', 'w') as f:
            json.dump(self.prompts, f)
            
    def setup_commands(self):
        @self.command(name='註冊')
        async def register_prompt(ctx, char_name: str, *, prompt: str):
            user_id = str(ctx.author.id)
            if user_id not in self.prompts:
                self.prompts[user_id] = {}
                
            self.prompts[user_id][char_name] = {
                'prompt': prompt,
                'schedule': None
            }
            self.save_prompts()
            
            await ctx.send(f"野生的 {char_name} 出現了！")

        @self.command(name='幫助')
        async def command_help(ctx):
            await ctx.send(f"輸入指令：\n!註冊 <角色名稱> <背景設定>：設定角色\n!排程 <角色名稱> <HH:MM>：讓角色在指定時間對你催稿\n!互動 <角色名稱>：讓角色立刻對你催稿\n!清單：檢查當前的角色和排程\n!刪除 <角色名稱>：刪除已註冊的角色")

        @self.command(name='排程')
        async def set_schedule(ctx, char_name: str, time: str):
            user_id = str(ctx.author.id)
            if user_id not in self.prompts or char_name not in self.prompts[user_id]:
                await ctx.send(f"{char_name}？這誰？")
                return
                
            try:
                hour, minute = map(int, time.split(':'))
                self.prompts[user_id][char_name]['schedule'] = f"{minute} {hour} * * *"
                self.save_prompts()
                
                # Add to scheduler
                self.scheduler.add_job(
                    self.send_reminder,
                    CronTrigger.from_crontab(self.prompts[user_id][char_name]['schedule']),
                    args=[ctx.channel.id, user_id, char_name]
                )
                
                await ctx.send(f"{char_name}會在 {time} 時對你催稿!")
            except ValueError:
                await ctx.send("看不懂你在打甚麼鬼，請依格式輸入 HH:MM 來設定時間。")
                
        @self.command(name='互動')
        async def manual_remind(ctx, char_name: str):
            user_id = str(ctx.author.id)
            if user_id not in self.prompts or char_name not in self.prompts[user_id]:
                await ctx.send(f"{char_name}？這誰？")
                return
                
            await self.send_reminder(ctx.channel.id, user_id, char_name)
            
        @self.command(name='清單')
        async def list_prompts(ctx):
            user_id = str(ctx.author.id)
            if user_id not in self.prompts or not self.prompts[user_id]:
                await ctx.send(f"你還沒有註冊任何角色喔。")
                return

            chars = [f"- {name} (排程: {info['schedule'] or '無。'})"
                    for name, info in self.prompts[user_id].items()]
            await ctx.send(f"你的角色列表 : \n" + "\n".join(chars))
            
        @self.command(name='刪除')
        async def delete_prompt(ctx, char_name: str):
            user_id = str(ctx.author.id)
            if user_id in self.prompts and char_name in self.prompts[user_id]:
                del self.prompts[user_id][char_name]
                self.save_prompts()
                await ctx.send(f" 『啪！』的一聲， {char_name} 消失在虛空之中，與之一併消散的是他催你稿的記憶。")
            else:
                await ctx.send(f"{char_name}？這誰？")
                
    async def send_reminder(self, channel_id, user_id, char_name):
        channel = self.get_channel(channel_id)
        user = await self.fetch_user(int(user_id))
        member = await channel.guild.fetch_member(int(user_id)) # 使用 fetch_member
        user_nickname = member.display_name if member else user.name# 取得暱稱，如果沒有設定則使用使用者名稱

        prompt = self.prompts[user_id][char_name]['prompt']

        try:
            final_prompt = self.reminder_template.format_messages(char_name=char_name, prompt=prompt, user_nickname=user_nickname)
            response = await self.llm.agenerate([final_prompt])
            formatted_reminder = response.generations[0][0].text.strip()
            control_chars = "<|im_start|>assistant<|im_sep|>"
            if formatted_reminder.startswith(control_chars): #先判斷是否以此開頭，避免沒有控制字元時出錯
                cleaned_reminder = formatted_reminder[len(control_chars):].strip() #字串切片

        except Exception as e:
            print(f"Error generating response: {e}")
            formatted_reminder = "抱歉，機器人好像故障了，快點叫官官救我！"

        await channel.send(f"{user.mention} {cleaned_reminder}")
        
    async def setup_hook(self):
        # Start scheduler
        self.scheduler.start()
        
        # Setup scheduled reminders from saved prompts
        for user_id, chars in self.prompts.items():
            for char_name, info in chars.items():
                if info['schedule']:
                    self.scheduler.add_job(
                        self.send_reminder,
                        CronTrigger.from_crontab(info['schedule']),
                        args=[self.get_channel(int(user_id)), user_id, char_name]
                    )
from nextcord.ext import commands
from nextcord.ext import tasks
from core import constants
from events.impl import message_event
from events.impl.coin_activity import VoiceCoinActivity
from events.impl.daily_event import DailyEvent

class Discord_Event(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message_event = message_event.MessageEvent()
        self.voice_coin_activity = VoiceCoinActivity(bot)
        self.daily_event = DailyEvent()
        self.voice_reward_loop.start()
        self.daily_event_loop.start()

    def cog_unload(self):
        self.voice_reward_loop.cancel()
        self.daily_event_loop.cancel()
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        await self.message_event.on_message(message)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        await self.message_event.on_message_delete(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.message_event.on_message_edit(before, after)

    @tasks.loop(seconds=constants.VOICE_REWARD_CHECK_INTERVAL_SECONDS)
    async def voice_reward_loop(self):
        await self.voice_coin_activity.check_voice_channels()

    @voice_reward_loop.before_loop
    async def before_voice_reward_loop(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=constants.DAILY_EVENT_CHECK_INTERVAL_SECONDS)
    async def daily_event_loop(self):
        await self.daily_event.run_if_needed()

    @daily_event_loop.before_loop
    async def before_daily_event_loop(self):
        await self.bot.wait_until_ready()
        
def setup(bot):
    bot.add_cog(Discord_Event(bot))

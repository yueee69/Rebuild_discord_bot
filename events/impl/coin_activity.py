import re

from core import constants
from managers.user_manager import UserManager


CUSTOM_EMOJI_PATTERN = re.compile(r"<:\w+:\d+>")


class MessageCoinActivity:
    def __init__(self, user_manager: UserManager | None = None):
        self.user_manager = user_manager or UserManager()

    async def on_message(self, message):
        if self._should_ignore(message):
            return

        self.user_manager.reset_daily_activity_if_needed()
        coin = self.calculate_message_coin(message.content)
        self.user_manager.add_chat_coin(message.author.id, coin)

    async def on_message_delete(self, message):
        if self._should_ignore(message):
            return

        self.user_manager.reset_daily_activity_if_needed()
        coin = self.calculate_message_coin(message.content)
        self.user_manager.add_chat_coin(message.author.id, -coin)

    async def on_message_edit(self, before, after):
        if self._should_ignore(after):
            return

        self.user_manager.reset_daily_activity_if_needed()
        before_coin = self.calculate_message_coin(before.content)
        after_coin = self.calculate_message_coin(after.content)
        self.user_manager.add_chat_coin(after.author.id, after_coin - before_coin)

    @staticmethod
    def calculate_message_coin(content: str) -> int:
        text = content or ""
        custom_emoji_count = len(CUSTOM_EMOJI_PATTERN.findall(text))
        plain_text_length = len(CUSTOM_EMOJI_PATTERN.sub("", text))
        return (plain_text_length + custom_emoji_count) * constants.MESSAGE_COIN_PER_CHARACTER

    @staticmethod
    def _should_ignore(message) -> bool:
        return (
            message is None
            or message.author is None
            or message.author.bot
            or message.guild is None
        )


class VoiceCoinActivity:
    def __init__(self, bot, user_manager: UserManager | None = None):
        self.bot = bot
        self.user_manager = user_manager or UserManager()

    async def check_voice_channels(self):
        self.user_manager.reset_daily_activity_if_needed()

        for guild in self.bot.guilds:
            if guild.id not in constants.ENABLE_COMMAND_USE_GUILDS:
                continue

            for channel in guild.voice_channels:
                members = [member for member in channel.members if not member.bot]
                if len(members) <= 1:
                    continue

                for member in members:
                    await self._reward_member(member)

    async def _reward_member(self, member):
        voice_state = member.voice
        if voice_state is None or voice_state.self_deaf:
            return

        user = self.user_manager.get(member.id, create_if_missing=False)
        if not user:
            return

        if voice_state.self_stream or voice_state.self_video:
            stream_reward = self._remaining_reward(
                user.stream,
                constants.DAILY_STREAM_COIN_LIMIT,
                constants.STREAM_COIN_PER_CHECK,
            )
            if stream_reward:
                self.user_manager.add_stream_coin(member.id, stream_reward)

        voice_reward = self._remaining_reward(
            user.voice,
            constants.DAILY_VOICE_COIN_LIMIT,
            constants.VOICE_COIN_PER_CHECK,
        )
        if voice_reward:
            self.user_manager.add_voice_coin(member.id, voice_reward)

    @staticmethod
    def _remaining_reward(current: int, limit: int, reward: int) -> int:
        if current >= limit:
            return 0
        return min(reward, limit - current)

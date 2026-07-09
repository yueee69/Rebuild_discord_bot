import asyncio
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import mafic
import nextcord
from nextcord import Interaction

from core import constants


class RepeatMode(Enum):
    NORMAL = "普通播放"
    SINGLE = "單曲循環"
    RANDOM = "隨機播放"


@dataclass
class QueuedTrack:
    track: mafic.Track
    requester_id: int
    requester_name: str


@dataclass
class GuildMusicState:
    queue: list[QueuedTrack] = field(default_factory=list)
    current: Optional[QueuedTrack] = None
    history: list[QueuedTrack] = field(default_factory=list)
    repeat_mode: RepeatMode = RepeatMode.NORMAL
    volume: int = 50
    panel_message: Optional[nextcord.Message] = None


class MusicService:
    SOURCE_EMOJIS = {
        "spotify": ("spotify", 1524523714476114061, "🟢"),
        "youtube": ("youtube", 1524523785355788479, "▶️"),
        "default": "🎵",
    }

    def __init__(self, bot):
        self.bot = bot
        self.node_ready = asyncio.Event()
        self.node_error: str | None = None
        self.states: dict[int, GuildMusicState] = {}
        self.bot.loop.create_task(self.add_lavalink_node())

    async def add_lavalink_node(self):
        if not hasattr(self.bot, "mafic_pool"):
            self.bot.mafic_pool = mafic.NodePool(self.bot)

        try:
            node = self.bot.mafic_pool.label_to_node.get(constants.LAVALINK_LABEL)
            if node:
                self.node_ready.set()
                self.node_error = None
                return

            await self.bot.mafic_pool.create_node(
                host=constants.LAVALINK_HOST,
                port=constants.LAVALINK_PORT,
                label=constants.LAVALINK_LABEL,
                password=constants.LAVALINK_PASSWORD,
                secure=constants.LAVALINK_SECURE,
            )
            self.node_ready.set()
            self.node_error = None
            print(f"(music) Lavalink node connected: {constants.LAVALINK_LABEL}")
        except Exception as exc:
            self.node_error = str(exc)
            print(f"(music) Lavalink node connect failed: {exc}")

    async def connect_to_author_voice(self, interaction: Interaction) -> mafic.Player | None:
        if not await self.ensure_node_ready(interaction):
            return None

        voice = getattr(interaction.user, "voice", None)
        if not voice or not voice.channel:
            await interaction.followup.send("你需要先加入一個語音房。", ephemeral=True)
            return None

        player = interaction.guild.voice_client
        if player:
            if not isinstance(player, mafic.Player):
                await interaction.followup.send("請先讓機器人離開語音房。", ephemeral=True)
                return None

            if player.channel != voice.channel:
                try:
                    await player.disconnect()
                    player = await voice.channel.connect(cls=mafic.Player)
                    await self.deafen_self(interaction.guild)
                except nextcord.HTTPException as exc:
                    await interaction.followup.send(f"切換語音房失敗：`{exc}`", ephemeral=True)
                    return None
            return player

        try:
            player = await voice.channel.connect(cls=mafic.Player)
            await self.deafen_self(interaction.guild)
            return player
        except nextcord.HTTPException as exc:
            await interaction.followup.send(f"加入語音房失敗：`{exc}`", ephemeral=True)
            return None

    async def deafen_self(self, guild: nextcord.Guild):
        try:
            await guild.me.edit(deafen=True)
        except nextcord.HTTPException as exc:
            print(f"(music) failed to deafen self: {exc}")

    async def ensure_node_ready(self, interaction: Interaction) -> bool:
        if self.node_ready.is_set():
            return True

        if self.node_error:
            self.bot.loop.create_task(self.add_lavalink_node())

        try:
            await asyncio.wait_for(self.node_ready.wait(), timeout=8)
            return True
        except asyncio.TimeoutError:
            message = "Lavalink 節點尚未連線完成。"
            if self.node_error:
                message += f"\n錯誤：`{self.node_error}`"
            await interaction.followup.send(message, ephemeral=True)
            return False

    async def ensure_same_voice(self, interaction: Interaction) -> bool:
        player = self.get_player(interaction)
        if not player:
            await self.send_interaction_error(interaction, "我目前不在語音房。")
            return False

        user_voice = getattr(interaction.user, "voice", None)
        if not user_voice or not user_voice.channel:
            await self.send_interaction_error(interaction, "你需要先加入語音房，才可以操作音樂。")
            return False

        if user_voice.channel != player.channel:
            await self.send_interaction_error(interaction, f"你需要和我在同一個語音房 `{player.channel.name}` 才可以操作音樂。")
            return False

        return True

    async def send_interaction_error(self, interaction: Interaction, message: str):
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    def get_player(self, interaction: Interaction) -> mafic.Player | None:
        player = interaction.guild.voice_client
        if isinstance(player, mafic.Player):
            return player
        return None

    def get_state(self, guild_id: int) -> GuildMusicState:
        if guild_id not in self.states:
            self.states[guild_id] = GuildMusicState()
        return self.states[guild_id]

    async def fetch_tracks(self, player: mafic.Player, link: str, interaction: Interaction) -> tuple[list[mafic.Track], str | None]:
        try:
            result = await player.fetch_tracks(link)
        except Exception as exc:
            await interaction.followup.send(f"解析連結失敗：`{exc}`", ephemeral=True)
            return [], None

        if not result:
            await interaction.followup.send("找不到可以播放的音軌。", ephemeral=True)
            return [], None

        if isinstance(result, mafic.Playlist):
            if not result.tracks:
                await interaction.followup.send("這個歌單裡沒有可以播放的音軌。", ephemeral=True)
                return [], result.name
            return result.tracks, result.name

        tracks = list(result)
        if not tracks:
            await interaction.followup.send("找不到可以播放的音軌。", ephemeral=True)
            return [], None
        return tracks, None

    async def start_track(self, guild: nextcord.Guild, player: mafic.Player, queued: QueuedTrack):
        state = self.get_state(guild.id)
        state.current = queued
        await player.play(queued.track, volume=self.lavalink_volume(state.volume))

    async def play_next(self, guild: nextcord.Guild, player: mafic.Player):
        state = self.get_state(guild.id)
        if state.current:
            state.history.append(state.current)
            state.history = state.history[-10:]

        if state.repeat_mode == RepeatMode.SINGLE and state.current:
            await self.start_track(guild, player, state.current)
            return

        if not state.queue:
            state.current = None
            return

        await self.start_track(guild, player, self.pop_next_track(state))

    async def stop_and_clear(self, guild: nextcord.Guild, player: mafic.Player):
        state = self.get_state(guild.id)
        state.queue.clear()
        state.current = None
        await player.disconnect()

    def remove_queue_indexes(self, guild_id: int, indexes: list[int]) -> list[QueuedTrack]:
        state = self.get_state(guild_id)
        removed = []
        for index in sorted(set(indexes), reverse=True):
            if 0 <= index < len(state.queue):
                removed.append(state.queue.pop(index))
        return list(reversed(removed))

    def clear_queue(self, guild_id: int) -> int:
        state = self.get_state(guild_id)
        count = len(state.queue)
        state.queue.clear()
        return count

    def jump_to_queue_index(self, guild_id: int, index: int) -> QueuedTrack | None:
        state = self.get_state(guild_id)
        if 0 <= index < len(state.queue):
            return state.queue.pop(index)
        return None

    @staticmethod
    def lavalink_volume(user_volume: int) -> int:
        return int(user_volume / 4)

    @staticmethod
    def pop_next_track(state: GuildMusicState) -> QueuedTrack:
        if state.repeat_mode == RepeatMode.RANDOM and len(state.queue) > 1:
            return state.queue.pop(random.randrange(len(state.queue)))
        return state.queue.pop(0)

    @staticmethod
    def next_repeat_mode(mode: RepeatMode) -> RepeatMode:
        modes = [RepeatMode.NORMAL, RepeatMode.SINGLE, RepeatMode.RANDOM]
        return modes[(modes.index(mode) + 1) % len(modes)]

    @staticmethod
    def track_link(track: mafic.Track) -> str:
        title = getattr(track, "title", "未知歌曲")
        uri = getattr(track, "uri", None)
        return f"[{title}]({uri})" if uri else title

    @classmethod
    def track_display(cls, track: mafic.Track, bot=None) -> str:
        return f"{cls.track_source_icon(track, bot)} {cls.track_link(track)}"

    @classmethod
    def track_label(cls, track: mafic.Track, bot=None) -> str:
        title = getattr(track, "title", "未知歌曲")
        return f"{cls.track_source_icon(track, bot)} {title}"

    @classmethod
    def track_source_icon(cls, track: mafic.Track, bot=None) -> str:
        source_name = str(getattr(track, "source", "") or getattr(track, "source_name", "")).lower()
        uri = str(getattr(track, "uri", "") or "").lower()

        if "spotify" in source_name or "open.spotify.com" in uri:
            return cls.resolve_source_emoji("spotify", bot)
        if "youtube" in source_name or "youtu" in uri:
            return cls.resolve_source_emoji("youtube", bot)
        return cls.SOURCE_EMOJIS["default"]

    @classmethod
    def resolve_source_emoji(cls, source: str, bot=None) -> str:
        setting = cls.SOURCE_EMOJIS.get(source)
        if isinstance(setting, tuple):
            _, emoji_id, fallback = setting
            emoji = bot.get_emoji(emoji_id) if bot else None
            return str(emoji) if emoji else fallback
        return setting or cls.SOURCE_EMOJIS["default"]

    @staticmethod
    def format_duration(milliseconds: int) -> str:
        seconds = int(milliseconds / 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

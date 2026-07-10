import asyncio
import contextlib
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Awaitable, Callable, Optional

import lavalink
import nextcord
from nextcord import Interaction

from core import constants


class RepeatMode(Enum):
    NORMAL = "一般播放"
    SINGLE = "單曲循環"
    RANDOM = "隨機播放"


@dataclass
class QueuedTrack:
    track: lavalink.AudioTrack
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


PanelRefreshCallback = Callable[[nextcord.Guild], Awaitable[None]]
LAVALINK_VOLUME_DIVISOR = 6


class LavalinkVoiceClient(nextcord.VoiceProtocol):
    def __init__(self, client: nextcord.Client, channel: nextcord.abc.Connectable):
        super().__init__(client, channel)
        self._voice_state_received = asyncio.Event()
        self._voice_server_received = asyncio.Event()

    @property
    def lavalink_client(self) -> lavalink.Client:
        client = getattr(self.client, "lavalink", None)
        if not isinstance(client, lavalink.Client):
            raise RuntimeError("Lavalink client has not been initialized.")
        return client

    async def on_voice_state_update(self, data: dict) -> None:
        await self.lavalink_client.voice_update_handler({"t": "VOICE_STATE_UPDATE", "d": data})
        self._voice_state_received.set()

    async def on_voice_server_update(self, data: dict) -> None:
        await self.lavalink_client.voice_update_handler({"t": "VOICE_SERVER_UPDATE", "d": data})
        self._voice_server_received.set()

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        await self.channel.guild.change_voice_state(channel=self.channel, self_deaf=True)
        await asyncio.wait_for(
            asyncio.gather(self._voice_state_received.wait(), self._voice_server_received.wait()),
            timeout=timeout,
        )

    async def disconnect(self, *, force: bool) -> None:
        with contextlib.suppress(nextcord.HTTPException):
            await self.channel.guild.change_voice_state(channel=None)
        self.cleanup()


class MusicService:
    SOURCE_EMOJIS = {
        "spotify": ("spotify", 1524523714476114061, "[Spotify]"),
        "youtube": ("youtube", 1524523785355788479, "[YouTube]"),
        "default": "[Music]",
    }

    def __init__(self, bot):
        self.bot = bot
        self.client: lavalink.Client | None = None
        self.node_ready = asyncio.Event()
        self.node_error: str | None = None
        self.states: dict[int, GuildMusicState] = {}
        self.panel_refresh_callback: PanelRefreshCallback | None = None
        self._event_hooks_registered = False
        self.bot.loop.create_task(self.add_lavalink_node())

    async def add_lavalink_node(self):
        try:
            await self.bot.wait_until_ready()
            client = self._get_or_create_client()
            node = next((node for node in client.node_manager.nodes if node.name == constants.LAVALINK_LABEL), None)
            if node:
                await self._wait_for_node_ready(node)
                self.node_ready.set()
                self.node_error = None
                return

            node = client.add_node(
                host=constants.LAVALINK_HOST,
                port=constants.LAVALINK_PORT,
                password=constants.LAVALINK_PASSWORD,
                region=constants.LAVALINK_REGION,
                name=constants.LAVALINK_LABEL,
                ssl=constants.LAVALINK_SECURE,
            )
            await self._wait_for_node_ready(node)
            self.node_ready.set()
            self.node_error = None
            print(f"(music) Lavalink node connected: {constants.LAVALINK_LABEL}")
        except Exception as exc:
            self.node_error = str(exc)
            print(f"(music) Lavalink node connect failed: {exc}")

    async def _wait_for_node_ready(self, node: lavalink.Node, timeout: float = 20) -> None:
        deadline = self.bot.loop.time() + timeout
        while self.bot.loop.time() < deadline:
            if node.available and node.session_id:
                return
            await asyncio.sleep(0.25)

        raise RuntimeError(f"Lavalink node {node.name} did not become ready within {timeout:g}s.")

    def _get_or_create_client(self) -> lavalink.Client:
        if self.client:
            return self.client

        user_id = self._bot_user_id()
        client = getattr(self.bot, "lavalink", None)
        if not isinstance(client, lavalink.Client):
            client = lavalink.Client(user_id=user_id)
            self.bot.lavalink = client

        self.client = client
        self._register_event_hooks(client)
        return client

    def _bot_user_id(self) -> int:
        user = self.bot.user
        if user:
            return user.id

        app_id = getattr(self.bot, "application_id", None)
        if app_id:
            return int(app_id)

        raise RuntimeError("Bot user is not ready yet; reload the music cog after the bot is ready.")

    def _register_event_hooks(self, client: lavalink.Client):
        if self._event_hooks_registered:
            return

        old_hooks = getattr(self.bot, "_music_lavalink_event_hooks", None)
        if old_hooks:
            for event, hook in old_hooks:
                client.remove_event_hooks(events=[event], hooks=[hook])

        hooks = [
            (lavalink.TrackEndEvent, self._handle_track_end),
            (lavalink.TrackExceptionEvent, self._handle_track_exception),
            (lavalink.TrackStuckEvent, self._handle_track_stuck),
        ]
        client.add_event_hook(self._handle_track_end, event=lavalink.TrackEndEvent)
        client.add_event_hook(self._handle_track_exception, event=lavalink.TrackExceptionEvent)
        client.add_event_hook(self._handle_track_stuck, event=lavalink.TrackStuckEvent)
        self.bot._music_lavalink_event_hooks = hooks
        self._event_hooks_registered = True

    async def connect_to_author_voice(self, interaction: Interaction) -> lavalink.DefaultPlayer | None:
        if not await self.ensure_node_ready(interaction):
            return None

        voice = getattr(interaction.user, "voice", None)
        if not voice or not voice.channel:
            await interaction.followup.send("請先加入一個語音頻道。", ephemeral=True)
            return None

        player = self.client.player_manager.create(interaction.guild.id)
        voice_client = interaction.guild.voice_client
        bot_voice = getattr(interaction.guild.me, "voice", None)

        if bot_voice and bot_voice.channel and not voice_client:
            await interaction.guild.change_voice_state(channel=None)
            await asyncio.sleep(0.5)

        if voice_client and not isinstance(voice_client, LavalinkVoiceClient):
            await interaction.followup.send("目前語音連線不是 Lavalink 播放器，請先讓機器人離開後再試。", ephemeral=True)
            return None

        if voice_client and voice_client.channel.id != voice.channel.id:
            await voice_client.disconnect(force=True)
            voice_client = None

        if not voice_client:
            try:
                await voice.channel.connect(cls=LavalinkVoiceClient)
            except (asyncio.TimeoutError, nextcord.ClientException, nextcord.HTTPException) as exc:
                await interaction.followup.send(f"加入語音頻道失敗：`{exc}`", ephemeral=True)
                return None

        return player

    async def ensure_node_ready(self, interaction: Interaction) -> bool:
        if self.node_ready.is_set():
            return True

        if self.node_error:
            self.bot.loop.create_task(self.add_lavalink_node())

        try:
            await asyncio.wait_for(self.node_ready.wait(), timeout=25)
            return True
        except asyncio.TimeoutError:
            message = "Lavalink 節點尚未連線，請稍後再試。"
            if self.node_error:
                message += f"\n錯誤：`{self.node_error}`"
            await interaction.followup.send(message, ephemeral=True)
            return False

    async def ensure_same_voice(self, interaction: Interaction) -> bool:
        player = self.get_player(interaction)
        if not player or not player.channel_id:
            await self.send_interaction_error(interaction, "機器人目前不在語音頻道。")
            return False

        user_voice = getattr(interaction.user, "voice", None)
        if not user_voice or not user_voice.channel:
            await self.send_interaction_error(interaction, "請先加入機器人所在的語音頻道。")
            return False

        if user_voice.channel.id != player.channel_id:
            channel = interaction.guild.get_channel(player.channel_id)
            channel_name = channel.name if channel else str(player.channel_id)
            await self.send_interaction_error(interaction, f"請到 `{channel_name}` 語音頻道後再操作。")
            return False

        return True

    async def send_interaction_error(self, interaction: Interaction, message: str):
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    def get_player(self, interaction: Interaction) -> lavalink.DefaultPlayer | None:
        if not interaction.guild or not self.client:
            return None
        return self.client.player_manager.get(interaction.guild.id)

    def get_state(self, guild_id: int) -> GuildMusicState:
        if guild_id not in self.states:
            self.states[guild_id] = GuildMusicState()
        return self.states[guild_id]

    async def fetch_tracks(
        self,
        player: lavalink.DefaultPlayer,
        link: str,
        interaction: Interaction,
    ) -> tuple[list[lavalink.AudioTrack], str | None]:
        try:
            result = await self.client.get_tracks(link, node=player.node)
        except Exception as exc:
            await interaction.followup.send(f"查詢歌曲失敗：`{exc}`", ephemeral=True)
            return [], None

        if result.load_type == lavalink.LoadType.ERROR:
            error = result.error.message if result.error else "未知錯誤"
            await interaction.followup.send(f"Lavalink 載入歌曲失敗：`{error}`", ephemeral=True)
            return [], None

        if result.load_type == lavalink.LoadType.EMPTY or not result.tracks:
            await interaction.followup.send("找不到可播放的歌曲。", ephemeral=True)
            return [], None

        if result.load_type == lavalink.LoadType.PLAYLIST:
            playlist_name = result.playlist_info.name or "playlist"
            return list(result.tracks), playlist_name

        return [result.tracks[0]], None

    async def start_track(self, guild: nextcord.Guild, player: lavalink.DefaultPlayer, queued: QueuedTrack):
        state = self.get_state(guild.id)
        state.current = queued
        queued.track.requester = queued.requester_id
        await player.play(queued.track, volume=self.effective_volume(state.volume))

    async def play_next(self, guild: nextcord.Guild, player: lavalink.DefaultPlayer):
        state = self.get_state(guild.id)
        if state.current:
            state.history.append(state.current)
            state.history = state.history[-10:]

        if state.repeat_mode == RepeatMode.SINGLE and state.current:
            await self.start_track(guild, player, state.current)
            return

        if not state.queue:
            state.current = None
            await player.stop()
            return

        await self.start_track(guild, player, self.pop_next_track(state))

    async def stop_and_clear(self, guild: nextcord.Guild, player: lavalink.DefaultPlayer):
        state = self.get_state(guild.id)
        state.queue.clear()
        state.current = None
        await self.disconnect_player(guild, player)

    async def disconnect_player(self, guild: nextcord.Guild, player: lavalink.DefaultPlayer):
        voice_client = guild.voice_client
        if voice_client:
            await voice_client.disconnect(force=True)
        else:
            await guild.change_voice_state(channel=None)
        if self.client:
            await self.client.player_manager.destroy(player.guild_id)

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
    def pop_next_track(state: GuildMusicState) -> QueuedTrack:
        if state.repeat_mode == RepeatMode.RANDOM and len(state.queue) > 1:
            return state.queue.pop(random.randrange(len(state.queue)))
        return state.queue.pop(0)

    @staticmethod
    def effective_volume(user_volume: int) -> int:
        if user_volume <= 0:
            return 0
        return max(1, user_volume // LAVALINK_VOLUME_DIVISOR)

    @staticmethod
    def next_repeat_mode(mode: RepeatMode) -> RepeatMode:
        modes = [RepeatMode.NORMAL, RepeatMode.SINGLE, RepeatMode.RANDOM]
        return modes[(modes.index(mode) + 1) % len(modes)]

    async def _handle_track_end(self, event: lavalink.TrackEndEvent):
        print(f"(music) track ended: reason={event.reason.value}")
        if event.reason in {lavalink.EndReason.REPLACED, lavalink.EndReason.CLEANUP, lavalink.EndReason.STOPPED}:
            return

        await self._advance_after_event(event.player)

    async def _handle_track_exception(self, event: lavalink.TrackExceptionEvent):
        await self._advance_after_event(event.player)

    async def _handle_track_stuck(self, event: lavalink.TrackStuckEvent):
        await self._advance_after_event(event.player)

    async def _advance_after_event(self, player: lavalink.DefaultPlayer):
        guild = self.bot.get_guild(player.guild_id)
        if not guild:
            return

        await self.play_next(guild, player)
        if self.panel_refresh_callback:
            await self.panel_refresh_callback(guild)

    @staticmethod
    def track_link(track: lavalink.AudioTrack) -> str:
        title = getattr(track, "title", "未知歌曲")
        uri = getattr(track, "uri", None)
        return f"[{title}]({uri})" if uri else title

    @classmethod
    def track_display(cls, track: lavalink.AudioTrack, bot=None) -> str:
        return f"{cls.track_source_icon(track, bot)} {cls.track_link(track)}"

    @classmethod
    def track_label(cls, track: lavalink.AudioTrack, bot=None) -> str:
        title = getattr(track, "title", "未知歌曲")
        return f"{cls.track_source_icon(track, bot)} {title}"

    @classmethod
    def track_source_icon(cls, track: lavalink.AudioTrack, bot=None) -> str:
        source_name = str(getattr(track, "source_name", "") or getattr(track, "source", "")).lower()
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

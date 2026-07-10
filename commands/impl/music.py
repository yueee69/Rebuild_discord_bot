import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import application_checks, commands

from core import constants
from features.music.music_service import MusicService, QueuedTrack, RepeatMode
from commands.base_command import Cog_Extension
from views.music_views import (
    MusicPanelPage,
    MusicQueuePage,
    component_kwargs,
    edit_kwargs,
    message_components,
)


class Music(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        self.service = MusicService(bot)
        self.service.panel_refresh_callback = self.refresh_panel

    @nextcord.slash_command(name="加入語音", description="讓機器人加入你目前所在的語音房", guild_ids=constants.ENABLE_COMMAND_USE_GUILDS)
    @application_checks.guild_only()
    async def join_voice(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        player = await self.service.connect_to_author_voice(interaction)
        if not player:
            return

        channel = interaction.guild.get_channel(player.channel_id) if player.channel_id else None
        channel_name = channel.name if channel else "目前語音頻道"
        await interaction.followup.send(
            **component_kwargs(message_components(f"✅ 成功加入 `{channel_name}` 語音房！"))
        )

    @nextcord.slash_command(name="播放", description="透過連結播放或加入佇列", guild_ids=constants.ENABLE_COMMAND_USE_GUILDS)
    @application_checks.guild_only()
    async def play(
        self,
        interaction: Interaction,
        link: str = SlashOption(name="連結", description="貼上 Youtube 或是 Spotify 歌曲連結", required=True),
    ):
        await interaction.response.defer()
        player = await self.service.connect_to_author_voice(interaction)
        if not player:
            return

        tracks, playlist_name = await self.service.fetch_tracks(player, link, interaction)
        if not tracks:
            return

        state = self.service.get_state(interaction.guild.id)
        queued_tracks = [
            QueuedTrack(
                track=track,
                requester_id=interaction.user.id,
                requester_name=interaction.user.display_name,
            )
            for track in tracks
        ]

        if state.current and player.current:
            state.queue.extend(queued_tracks)
            await interaction.followup.send(
                **component_kwargs(message_components(self.build_add_tracks_message(queued_tracks, playlist_name), ephemeral=False))
            )
            await self.refresh_panel(interaction.guild)
            return

        if state.current and not player.current:
            state.current = None

        first_track = queued_tracks.pop(0)
        state.queue.extend(queued_tracks)
        await self.service.start_track(interaction.guild, player, first_track)
        state.panel_message = await interaction.channel.send(
            **edit_kwargs(
                MusicPanelPage(
                    self,
                    interaction.guild,
                    content=self.build_start_tracks_message(first_track, queued_tracks, playlist_name),
                ).get_components()
            )
        )
        await interaction.followup.send(
            **component_kwargs(message_components("✅ 已建立音樂控制面板。"))
        )

    @nextcord.slash_command(name="音樂面板", description="顯示目前播放狀態與控制面板", guild_ids=constants.ENABLE_COMMAND_USE_GUILDS)
    @application_checks.guild_only()
    async def music_panel(self, interaction: Interaction):
        if not await self.service.ensure_same_voice(interaction):
            return

        state = self.service.get_state(interaction.guild.id)
        if not state.current:
            await interaction.response.send_message(**component_kwargs(message_components("目前沒有正在播放的歌曲。")))
            return

        state.panel_message = await interaction.channel.send(
            **edit_kwargs(MusicPanelPage(self, interaction.guild).get_components())
        )
        await interaction.response.send_message(**component_kwargs(message_components("✅ 已重新建立音樂控制面板。")))

    @nextcord.slash_command(name="音量", description="調整音樂音量", guild_ids=constants.ENABLE_COMMAND_USE_GUILDS)
    @application_checks.guild_only()
    async def volume(
        self,
        interaction: Interaction,
        value: int = SlashOption(name="音量", description="0-100", min_value=0, max_value=100, required=True),
    ):
        if not await self.service.ensure_same_voice(interaction):
            return

        await self.set_volume(interaction, value)

    @nextcord.slash_command(name="離開語音", description="停止播放並離開語音房", guild_ids=constants.ENABLE_COMMAND_USE_GUILDS)
    @application_checks.guild_only()
    async def leave_voice(self, interaction: Interaction):
        if not await self.service.ensure_same_voice(interaction):
            return

        player = self.service.get_player(interaction)
        if not player:
            await interaction.response.send_message(**component_kwargs(message_components("我目前不在語音房。")))
            return

        await self.service.stop_and_clear(interaction.guild, player)
        await interaction.response.send_message(**component_kwargs(message_components("✅ 已停止播放並離開語音房。")))
        await self.refresh_panel(interaction.guild)

    async def toggle_pause(self, interaction: Interaction):
        player = self.service.get_player(interaction)
        if not player:
            await interaction.response.send_message(**component_kwargs(message_components("我目前不在語音房。")))
            return

        await player.set_pause(not player.paused)
        action = "暫停" if player.paused else "繼續播放"
        await interaction.response.edit_message(
            **edit_kwargs(
                MusicPanelPage(
                    self,
                    interaction.guild,
                    content=f"✅ 音樂已{action}！\n操作者：{interaction.user.display_name}",
                ).get_components()
            )
        )

    async def skip(self, interaction: Interaction):
        player = self.service.get_player(interaction)
        if not player:
            await interaction.response.send_message(**component_kwargs(message_components("我目前不在語音房。")))
            return

        state = self.service.get_state(interaction.guild.id)
        if state.repeat_mode == RepeatMode.SINGLE and state.current:
            await interaction.response.defer()
            await self.service.start_track(interaction.guild, player, state.current)
            await self.refresh_panel(interaction.guild)
            await interaction.followup.send(
                **component_kwargs(
                    message_components(f"✅ 單曲循環中，已重新播放：{MusicService.track_display(state.current.track, self.bot)}")
                )
            )
            return

        if not state.queue:
            await interaction.response.send_message(**component_kwargs(message_components("目前佇列沒有下一首，音樂會繼續播放。")))
            await self.refresh_panel(interaction.guild)
            return

        await interaction.response.defer()
        if state.current:
            state.history.append(state.current)
            state.history = state.history[-10:]

        next_track = self.service.pop_next_track(state)
        await self.service.start_track(interaction.guild, player, next_track)
        await self.refresh_panel(interaction.guild)
        await interaction.followup.send(
            **component_kwargs(message_components(f"✅ 已跳過目前歌曲\n正在播放：{MusicService.track_display(next_track.track, self.bot)}"))
        )

    async def toggle_repeat(self, interaction: Interaction):
        state = self.service.get_state(interaction.guild.id)
        state.repeat_mode = self.service.next_repeat_mode(state.repeat_mode)
        await interaction.response.edit_message(
            **edit_kwargs(
                MusicPanelPage(
                    self,
                    interaction.guild,
                    content=f"✅ 成功把播放狀態改為 `{state.repeat_mode.value}`\n操作者：{interaction.user.display_name}",
                ).get_components()
            )
        )

    async def show_queue(self, interaction: Interaction):
        state = self.service.get_state(interaction.guild.id)
        if not state.queue:
            await interaction.response.send_message(**component_kwargs(message_components("目前佇列是空的。")))
            return

        await interaction.response.send_message(**component_kwargs(MusicQueuePage(self, interaction.guild, 0).get_components()))

    async def show_history(self, interaction: Interaction):
        state = self.service.get_state(interaction.guild.id)
        if not state.history:
            await interaction.response.send_message(**component_kwargs(message_components("目前還沒有播放歷史。")))
            return

        lines = [
            f"{idx}. {MusicService.track_display(item.track, self.bot)} | {item.requester_name}"
            for idx, item in enumerate(reversed(state.history[-10:]), start=1)
        ]
        await interaction.response.send_message(**component_kwargs(message_components("\n".join(lines))))

    async def stop_and_disconnect(self, interaction: Interaction):
        player = self.service.get_player(interaction)
        if not player:
            await interaction.response.send_message(**component_kwargs(message_components("我目前不在語音房。")))
            return

        await self.service.stop_and_clear(interaction.guild, player)
        await interaction.response.edit_message(
            **edit_kwargs(MusicPanelPage(self, interaction.guild, content="✅ 已停止播放並離開語音房。", include_view=False).get_components())
        )

    async def set_volume(self, interaction: Interaction, value: int, edit_panel: bool = False):
        if value < 0 or value > 100:
            await interaction.response.send_message(**component_kwargs(message_components("請輸入 0 到 100 的整數。")))
            return

        player = self.service.get_player(interaction)
        if not player:
            await interaction.response.send_message(**component_kwargs(message_components("我目前不在語音房。")))
            return

        state = self.service.get_state(interaction.guild.id)
        state.volume = value
        await player.set_volume(MusicService.effective_volume(value))

        content = f"✅ 成功修改音量！\n{interaction.user.display_name} 把音量修改到了 **{value if value != 0 else '靜音'}**"
        if edit_panel and not interaction.response.is_done():
            await interaction.response.edit_message(
                **edit_kwargs(MusicPanelPage(self, interaction.guild, content=content).get_components())
            )
        elif not interaction.response.is_done():
            await interaction.response.send_message(**component_kwargs(message_components(content)))
        else:
            await interaction.followup.send(**component_kwargs(message_components(content)))

        if not edit_panel:
            await self.refresh_panel(interaction.guild)

    async def refresh_panel(self, guild: nextcord.Guild):
        state = self.service.get_state(guild.id)
        if not state.panel_message:
            return

        try:
            await state.panel_message.edit(
                **edit_kwargs(MusicPanelPage(self, guild).get_components())
            )
        except nextcord.NotFound:
            state.panel_message = None
        except nextcord.HTTPException as exc:
            if getattr(exc, "status", None) == 401 or getattr(exc, "code", None) == 50027:
                state.panel_message = None
                return
            raise

    def build_add_tracks_message(self, tracks: list[QueuedTrack], playlist_name: str | None) -> str:
        if playlist_name:
            return f"✅ 成功加入歌單 `{playlist_name}`，共 {len(tracks)} 首歌。"

        return f"✅ 成功加入佇列：{MusicService.track_display(tracks[0].track, self.bot)}"

    def build_start_tracks_message(
        self,
        current: QueuedTrack,
        queued_tracks: list[QueuedTrack],
        playlist_name: str | None,
    ) -> str:
        if playlist_name:
            return (
                f"✅ 開始播放歌單 `{playlist_name}`\n"
                f"正在播放：{MusicService.track_display(current.track, self.bot)}\n"
                f"已加入佇列：{len(queued_tracks)} 首"
            )

        return f"✅ 開始播放：{MusicService.track_display(current.track, self.bot)}"



def setup(bot):
    bot.add_cog(Music(bot))

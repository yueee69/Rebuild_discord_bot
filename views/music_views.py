import math

import nextcord
from nextcord import Interaction

from features.music.music_service import GuildMusicState, MusicService, QueuedTrack
from .BASIC_VIEW import BASIC_VIEW


QUEUE_PAGE_SIZE = 10


def component_kwargs(components: tuple) -> dict:
    embed, view, ephemeral, content, *rest = components
    kwargs = {
        "ephemeral": ephemeral,
        **({"embed": embed} if embed else {}),
        **({"view": view} if view else {}),
        **({"content": content} if content else {}),
    }
    if rest:
        kwargs["file"] = rest[0]
    return kwargs


def edit_kwargs(components: tuple) -> dict:
    embed, view, _, content, *rest = components
    kwargs = {
        **({"embed": embed} if embed else {}),
        **({"view": view} if view else {}),
        **({"content": content} if content else {}),
    }
    if rest:
        kwargs["file"] = rest[0]
    return kwargs


class MusicHelpPage:
    @staticmethod
    def get_components() -> BASIC_VIEW:
        embed = nextcord.Embed(
            title="音樂機器人快速上手",
            description=(
                "先進語音房，輸入 `/播放` 貼上連結就能開始。\n"
                "YouTube、Spotify 單曲與歌單都會交給 Lavalink 解析，能不能播主要看目前節點支援。"
            ),
            color=nextcord.Colour.blurple(),
        )

        embed.add_field(
            name="最快播放流程",
            value=(
                "1. 你先加入一個語音房。\n"
                "2. `/播放 連結` 貼上單曲或歌單連結。\n"
                "3. 機器人會自動加入你的語音房，並建立控制面板。\n"
                "4. 後續再用 `/播放` 會直接加入佇列。"
            ),
            inline=False,
        )
        embed.add_field(
            name="常用指令",
            value=(
                "`/播放` 加歌或播放歌單\n"
                "`/加入語音` 只讓機器人先進語音房\n"
                "`/音樂面板` 重新叫出目前播放控制板\n"
                "`/音量` 直接設定 0-100 音量\n"
                "`/離開語音` 停止播放並清空音樂狀態"
            ),
            inline=False,
        )
        embed.add_field(
            name="控制面板",
            value=(
                "⏯️ 暫停 / 繼續\n"
                "⏭️ 下一首\n"
                "🔄 切換播放模式：普通播放、單曲循環、隨機播放\n"
                "📋 打開佇列分頁\n"
                "📜 查看歷史紀錄\n"
                "📢 調整音量\n"
                "⏹️ 停止並離開語音房"
            ),
            inline=False,
        )
        embed.add_field(
            name="佇列功能",
            value=(
                "佇列可以翻頁查看全部歌曲。\n"
                "也可以從當前頁面批量移除、清空佇列，或直接跳到指定歌曲。"
            ),
            inline=False,
        )
        embed.add_field(
            name="操作權限",
            value=(
                "控制面板、音量、佇列、離開等操作只允許和機器人在同一個語音房的人使用。\n"
                "如果機器人不在語音房，`/播放` 會以你目前所在的語音房為準。"
            ),
            inline=False,
        )
        return BASIC_VIEW.views(
            embed=embed,
            ephemeral=True,
            content="如果歌突然不能播，通常是 Lavalink 節點或來源網站限制，不一定是機器人指令壞掉。",
        )


class MusicPanelPage:
    def __init__(self, music, guild: nextcord.Guild, content: str = None, include_view: bool = True):
        self.music = music
        self.guild = guild
        self.content = content
        self.include_view = include_view
        self.state = music.service.get_state(guild.id)

    def get_components(self) -> BASIC_VIEW:
        view = MusicControlView(self.music, self.guild.id) if self.include_view and self.state.current else None
        return BASIC_VIEW.views(
            embed=self.build_embed(),
            view=view,
            content=self.content,
            clear_view=view is None,
        )

    def build_embed(self) -> nextcord.Embed:
        embed = nextcord.Embed(title="目前正在播放的歌曲訊息", color=nextcord.Colour.blurple())

        if not self.state.current:
            embed.description = "目前沒有正在播放的歌曲。"
            return embed

        track = self.state.current.track
        embed.add_field(name="歌曲平台 | 名稱", value=MusicService.track_display(track, self.music.bot), inline=False)
        embed.add_field(name="歌曲長度", value=MusicService.format_duration(getattr(track, "length", 0)), inline=True)
        embed.add_field(name="點歌用戶", value=self.state.current.requester_name, inline=True)
        embed.add_field(name="當前音量", value=str(self.state.volume), inline=True)
        embed.add_field(name="播放狀態", value=self.state.repeat_mode.value, inline=True)
        embed.add_field(name="下一首", value=self.queue_preview(), inline=False)

        artwork = getattr(track, "artwork_url", None)
        if artwork:
            embed.set_thumbnail(url=artwork)
        return embed

    def queue_preview(self) -> str:
        if not self.state.queue:
            return "目前沒有排隊歌曲。"

        lines = [
            f"{idx}. {truncate_track_label(self.music, item.track, 80)}"
            for idx, item in enumerate(self.state.queue[:5], start=1)
        ]
        if len(self.state.queue) > 5:
            lines.append(f"...還有 {len(self.state.queue) - 5} 首")
        return "\n".join(lines)


class MusicQueuePage:
    def __init__(self, music, guild: nextcord.Guild, page: int = 0, content: str = None, ephemeral: bool = True):
        self.music = music
        self.guild = guild
        self.page = page
        self.content = content
        self.ephemeral = ephemeral
        self.state = music.service.get_state(guild.id)

    def get_components(self) -> BASIC_VIEW:
        return BASIC_VIEW.views(
            embed=self.build_embed(),
            view=QueuePageView(self.music, self.guild.id, self.page),
            ephemeral=self.ephemeral,
            content=self.content,
        )

    def build_embed(self) -> nextcord.Embed:
        total = len(self.state.queue)
        max_page = max(0, (total - 1) // QUEUE_PAGE_SIZE)
        page = max(0, min(self.page, max_page))
        start = page * QUEUE_PAGE_SIZE
        page_items = self.state.queue[start:start + QUEUE_PAGE_SIZE]
        embed = nextcord.Embed(
            title=f"音樂佇列 第 {page + 1}/{max_page + 1} 頁",
            description=f"共 {total} 首",
            color=nextcord.Colour.blurple(),
        )

        if not page_items:
            embed.add_field(name="佇列", value="目前佇列是空的。", inline=False)
            return embed

        lines = []
        hidden = 0
        for idx, item in enumerate(page_items, start=1):
            title = truncate_track_label(self.music, item.track, 72)
            line = f"{start + idx}. {title} | {item.requester_name}"
            next_value = "\n".join([*lines, line])
            if len(next_value) > 1000:
                hidden += 1
                continue
            lines.append(line)

        if hidden:
            lines.append(f"...本頁還有 {hidden} 首因 Discord 長度限制未顯示")

        embed.add_field(name="歌曲", value="\n".join(lines), inline=False)
        return embed


def message_components(content: str, ephemeral: bool = True, clear_view: bool = False) -> BASIC_VIEW:
    return BASIC_VIEW.views(content=content, ephemeral=ephemeral, clear_view=clear_view)


def truncate_track_label(music, track, limit: int) -> str:
    text = MusicService.track_label(track, music.bot)
    return text if len(text) <= limit else text[:limit - 1] + "…"


class MusicControlView(nextcord.ui.View):
    def __init__(self, music, guild_id: int):
        super().__init__(timeout=None)
        self.music = music
        self.guild_id = guild_id

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.guild and interaction.guild.id == self.guild_id:
            return await self.music.service.ensure_same_voice(interaction)

        if not interaction.response.is_done():
            await interaction.response.send_message(
                **component_kwargs(message_components("這個控制面板不屬於目前伺服器。"))
            )
        return False

    @nextcord.ui.button(label="⏯️ 暫停/繼續", style=nextcord.ButtonStyle.primary, custom_id="music_toggle_pause")
    async def toggle_pause(self, button: nextcord.ui.Button, interaction: Interaction):
        await self.music.toggle_pause(interaction)

    @nextcord.ui.button(label="⏭️ 下一首", style=nextcord.ButtonStyle.primary, custom_id="music_skip")
    async def skip(self, button: nextcord.ui.Button, interaction: Interaction):
        await self.music.skip(interaction)

    @nextcord.ui.button(label="🔄 播放狀態", style=nextcord.ButtonStyle.primary, custom_id="music_repeat")
    async def repeat(self, button: nextcord.ui.Button, interaction: Interaction):
        await self.music.toggle_repeat(interaction)

    @nextcord.ui.button(label="📋 佇列", style=nextcord.ButtonStyle.primary, custom_id="music_queue", row=1)
    async def queue(self, button: nextcord.ui.Button, interaction: Interaction):
        await self.music.show_queue(interaction)

    @nextcord.ui.button(label="📜 歷史紀錄", style=nextcord.ButtonStyle.primary, custom_id="music_history", row=1)
    async def history(self, button: nextcord.ui.Button, interaction: Interaction):
        await self.music.show_history(interaction)

    @nextcord.ui.button(label="📢 調整音量", style=nextcord.ButtonStyle.primary, custom_id="music_volume", row=1)
    async def volume(self, button: nextcord.ui.Button, interaction: Interaction):
        state = self.music.service.get_state(self.guild_id)
        await interaction.response.send_modal(VolumeModal(self.music, state.volume))

    @nextcord.ui.button(label="⏹️ 停止離開", style=nextcord.ButtonStyle.danger, custom_id="music_stop", row=1)
    async def stop(self, button: nextcord.ui.Button, interaction: Interaction):
        await self.music.stop_and_disconnect(interaction)


class VolumeModal(nextcord.ui.Modal):
    def __init__(self, music, current_volume: int):
        super().__init__("調整音量！")
        self.music = music
        self.volume = nextcord.ui.TextInput(
            label="請輸入要調整的音量(0~100)",
            placeholder="0=靜音 50=一半音量 100=最大音量",
            default_value=str(current_volume),
            required=True,
            min_length=1,
            max_length=3,
        )
        self.add_item(self.volume)

    async def callback(self, interaction: Interaction):
        try:
            value = int(self.volume.value)
        except ValueError:
            await interaction.response.send_message(
                **component_kwargs(message_components(f'請輸入 0~100 的數字，你輸入的 "{self.volume.value}" 不是有效數字。'))
            )
            return

        await self.music.set_volume(interaction, value, edit_panel=True)


class QueuePageView(nextcord.ui.View):
    def __init__(self, music, guild_id: int, page: int = 0):
        super().__init__(timeout=180)
        self.music = music
        self.guild_id = guild_id
        self.page = page
        self._sync_buttons()

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.guild and interaction.guild.id == self.guild_id:
            return await self.music.service.ensure_same_voice(interaction)

        if not interaction.response.is_done():
            await interaction.response.send_message(
                **component_kwargs(message_components("這個佇列面板不屬於目前伺服器。"))
            )
        return False

    @nextcord.ui.button(label="上一頁", style=nextcord.ButtonStyle.primary, custom_id="music_queue_prev")
    async def prev_page(self, button: nextcord.ui.Button, interaction: Interaction):
        self.page = max(0, self.page - 1)
        self._sync_buttons()
        await interaction.response.edit_message(
            **edit_kwargs(MusicQueuePage(self.music, interaction.guild, self.page).get_components())
        )

    @nextcord.ui.button(label="下一頁", style=nextcord.ButtonStyle.primary, custom_id="music_queue_next")
    async def next_page(self, button: nextcord.ui.Button, interaction: Interaction):
        self.page = min(self.max_page, self.page + 1)
        self._sync_buttons()
        await interaction.response.edit_message(
            **edit_kwargs(MusicQueuePage(self.music, interaction.guild, self.page).get_components())
        )

    @nextcord.ui.button(label="🧹 批量移除", style=nextcord.ButtonStyle.primary, custom_id="music_queue_remove", row=1)
    async def remove_tracks(self, button: nextcord.ui.Button, interaction: Interaction):
        state = self.music.service.get_state(self.guild_id)
        start, end = self.page_bounds
        page_items = state.queue[start:end]
        if not page_items:
            await interaction.response.send_message(**component_kwargs(message_components("這一頁沒有可以移除的歌曲。")))
            return

        await interaction.response.send_message(
            **component_kwargs(
                BASIC_VIEW.views(
                    content="選擇要從佇列移除的歌曲：",
                    view=QueueRemoveSelectView(self.music, self.guild_id, self.page),
                    ephemeral=True,
                )
            )
        )

    @nextcord.ui.button(label="🎯 跳到指定歌曲", style=nextcord.ButtonStyle.primary, custom_id="music_queue_jump", row=1)
    async def jump_track(self, button: nextcord.ui.Button, interaction: Interaction):
        state = self.music.service.get_state(self.guild_id)
        start, end = self.page_bounds
        page_items = state.queue[start:end]
        if not page_items:
            await interaction.response.send_message(**component_kwargs(message_components("這一頁沒有可以跳轉的歌曲。")))
            return

        await interaction.response.send_message(
            **component_kwargs(
                BASIC_VIEW.views(
                    content="選擇要立即播放的歌曲：",
                    view=QueueJumpSelectView(self.music, self.guild_id, self.page),
                    ephemeral=True,
                )
            )
        )

    @nextcord.ui.button(label="🗑️ 清空佇列", style=nextcord.ButtonStyle.danger, custom_id="music_queue_clear", row=1)
    async def clear_queue(self, button: nextcord.ui.Button, interaction: Interaction):
        count = self.music.service.clear_queue(self.guild_id)
        await self.music.refresh_panel(interaction.guild)
        await interaction.response.edit_message(
            **edit_kwargs(
                MusicQueuePage(
                    self.music,
                    interaction.guild,
                    0,
                    content=f"✅ 已清空佇列，共移除 {count} 首歌。",
                ).get_components()
            )
        )

    @property
    def max_page(self) -> int:
        total = len(self.music.service.get_state(self.guild_id).queue)
        return max(0, math.ceil(total / QUEUE_PAGE_SIZE) - 1)

    @property
    def page_bounds(self) -> tuple[int, int]:
        start = self.page * QUEUE_PAGE_SIZE
        return start, start + QUEUE_PAGE_SIZE

    def _sync_buttons(self):
        self.prev_page.disabled = self.page <= 0
        self.next_page.disabled = self.page >= self.max_page


class QueueRemoveSelectView(nextcord.ui.View):
    def __init__(self, music, guild_id: int, page: int):
        super().__init__(timeout=120)
        self.add_item(QueueRemoveSelect(music, guild_id, page))


class QueueRemoveSelect(nextcord.ui.Select):
    def __init__(self, music, guild_id: int, page: int):
        self.music = music
        self.guild_id = guild_id
        self.page = page
        options = build_queue_options(music.service, guild_id, page)
        super().__init__(
            placeholder="選擇要移除的歌曲，可多選",
            min_values=1,
            max_values=max(1, len(options)),
            options=options,
        )

    async def callback(self, interaction: Interaction):
        indexes = [int(value) for value in self.values]
        removed = self.music.service.remove_queue_indexes(self.guild_id, indexes)
        await self.music.refresh_panel(interaction.guild)
        await interaction.response.edit_message(
            **edit_kwargs(message_components(f"✅ 已移除 {len(removed)} 首歌。", clear_view=True))
        )


class QueueJumpSelectView(nextcord.ui.View):
    def __init__(self, music, guild_id: int, page: int):
        super().__init__(timeout=120)
        self.add_item(QueueJumpSelect(music, guild_id, page))


class QueueJumpSelect(nextcord.ui.Select):
    def __init__(self, music, guild_id: int, page: int):
        self.music = music
        self.guild_id = guild_id
        options = build_queue_options(music.service, guild_id, page)
        super().__init__(
            placeholder="選擇要立即播放的歌曲",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: Interaction):
        player = self.music.service.get_player(interaction)
        if not player:
            await interaction.response.send_message(**component_kwargs(message_components("我目前不在語音房。")))
            return

        selected = self.music.service.jump_to_queue_index(self.guild_id, int(self.values[0]))
        if not selected:
            await interaction.response.edit_message(
                **edit_kwargs(message_components("找不到這首歌，可能已經被移除。", clear_view=True))
            )
            return

        state = self.music.service.get_state(self.guild_id)
        if state.current:
            state.history.append(state.current)
            state.history = state.history[-10:]

        await self.music.service.start_track(interaction.guild, player, selected)
        await self.music.refresh_panel(interaction.guild)
        await interaction.response.edit_message(
            **edit_kwargs(
                message_components(
                    f"✅ 已跳到：{MusicService.track_display(selected.track, self.music.bot)}",
                    clear_view=True,
                )
            )
        )


def build_queue_options(service: MusicService, guild_id: int, page: int) -> list[nextcord.SelectOption]:
    state = service.get_state(guild_id)
    start = page * QUEUE_PAGE_SIZE
    page_items = state.queue[start:start + QUEUE_PAGE_SIZE]
    options = []
    for offset, item in enumerate(page_items):
        index = start + offset
        title = getattr(item.track, "title", "未知歌曲")
        label = f"{index + 1}. {title}"[:100]
        description = f"點歌者：{item.requester_name}"[:100]
        options.append(nextcord.SelectOption(label=label, value=str(index), description=description))
    return options

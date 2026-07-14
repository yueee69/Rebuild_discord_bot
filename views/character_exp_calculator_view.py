from dataclasses import dataclass

import nextcord
from nextcord import Interaction

from utils.general import Toolkit

from core import constants
from features.character_exp_calculator import (
    CharacterExpResult,
    DiaryPlan,
    QuestExp,
    calculate_character_exp_plans,
    load_main_quests,
)
from .BASIC_VIEW import BASIC_VIEW


@dataclass(frozen=True)
class CharacterExpInput:
    current_level: int
    current_exp_percent: float
    target_level: int
    target_exp_percent: float


class CharacterExpCalculatorModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="角色經驗計算機")

        self.current_level = nextcord.ui.TextInput(
            label="目前等級",
            default_value="1",
            required=True,
            min_length=1,
            max_length=4,
        )
        self.current_exp_percent = nextcord.ui.TextInput(
            label="目前經驗百分比",
            default_value="0",
            required=True,
            min_length=1,
            max_length=6,
        )
        self.target_level = nextcord.ui.TextInput(
            label="目標等級",
            default_value=str(constants.CHARACTER_MAX_LEVEL),
            required=True,
            min_length=1,
            max_length=4,
        )
        self.target_exp_percent = nextcord.ui.TextInput(
            label="目標經驗百分比",
            default_value="0",
            required=True,
            min_length=1,
            max_length=6,
        )

        self.add_item(self.current_level)
        self.add_item(self.current_exp_percent)
        self.add_item(self.target_level)
        self.add_item(self.target_exp_percent)

    async def callback(self, interaction: Interaction):
        try:
            current_level = int(self.current_level.value)
            current_exp_percent = float(self.current_exp_percent.value)
            target_level = int(self.target_level.value)
            target_exp_percent = float(self.target_exp_percent.value)
        except ValueError as exc:
            await interaction.response.send_message(**_send_kwargs(BASIC_VIEW.views(content=str(exc), ephemeral=True)))
            return

        await interaction.response.defer()

        try:
            result = calculate_character_exp_plans(
                current_level=current_level,
                current_percent=current_exp_percent,
                target_level=target_level,
                target_percent=target_exp_percent,
            )
        except ValueError as exc:
            await interaction.followup.send(**_send_kwargs(BASIC_VIEW.views(content=str(exc))))
            return
        except Exception as exc:
            await interaction.followup.send(**_send_kwargs(BASIC_VIEW.views(content=f"計算失敗：`{exc}`")))
            return

        if result.required_exp == 0:
            await interaction.followup.send(**_send_kwargs(BASIC_VIEW.views(content="目標經驗沒有高於目前經驗，不需要跳任務。")))
            return

        if not result.plans:
            await interaction.followup.send(
                **_send_kwargs(
                    BASIC_VIEW.views(
                        content=f"在 {constants.CHARACTER_EXP_DIARY_ENUMERATION_LIMIT} 本日記內無法達成目標。"
                    )
                )
            )
            return

        quests = load_main_quests()
        user_input = CharacterExpInput(
            current_level=current_level,
            current_exp_percent=current_exp_percent,
            target_level=target_level,
            target_exp_percent=target_exp_percent,
        )
        view = DiaryPlanSelectView(result, quests, user_input)
        await interaction.followup.send(
            **_send_kwargs(view.build_summary_components())
        )


class DiaryPlanSelectView(nextcord.ui.View):
    def __init__(
        self,
        result: CharacterExpResult,
        quests: tuple[QuestExp, ...],
        user_input: CharacterExpInput,
    ):
        super().__init__(timeout=300)
        self.result = result
        self.quests = quests
        self.user_input = user_input
        self.plans = result.plans

        for chunk_index, start in enumerate(range(0, len(self.plans), 25), start=1):
            chunk = self.plans[start:start + 25]
            self.add_item(DiaryPlanSelect(self, chunk, start, chunk_index))

    def build_summary_components(self) -> BASIC_VIEW:
        fewest_diary_plan = self.plans[0]
        cheapest_plan = self.plans[-1]

        embed = nextcord.Embed(
            title="角色經驗計算機",
            description=(
                f"當前：{self.user_input.current_level} 等 {self.user_input.current_exp_percent:g}%\n"
                f"目標：{self.user_input.target_level} 等 {self.user_input.target_exp_percent:g}%\n"
                f"需要經驗：{self.result.required_exp:,}\n"
            ),
            color=Toolkit.randomcolor()
        )
        embed.add_field(
            name="最少日記可達成",
            value=_format_plan_brief(fewest_diary_plan),
            inline=True,
        )
        embed.add_field(
            name="目前枚舉內最低花費",
            value=_format_plan_brief(cheapest_plan),
            inline=True,
        )
        _add_plan_summary_fields(embed, self.plans)
        return BASIC_VIEW.views(embed=embed, view=self)

    def build_detail_components(self, *, selected_index: int) -> BASIC_VIEW:
        plan = self.plans[selected_index]
        embed = nextcord.Embed(
            title=f"日記方案：{plan.diaries} 本",
            description=_format_plan_brief(plan),
            color=Toolkit.randomcolor()
        )
        _add_segment_fields(embed, plan, self.quests)
        return BASIC_VIEW.views(embed=embed, view=None)


class DiaryPlanSelect(nextcord.ui.Select):
    def __init__(
        self,
        plan_view: DiaryPlanSelectView,
        plans: tuple[DiaryPlan, ...],
        offset: int,
        chunk_index: int,
    ):
        self.plan_view = plan_view
        options = [
            nextcord.SelectOption(
                label=f"最多 {plan.diaries} 本日記",
                description=f"花費 {plan.cost:,} 眾神幣",
                value=str(offset + index),
            )
            for index, plan in enumerate(plans)
        ]
        super().__init__(
            placeholder=f"選擇日記方案",
            min_values=1,
            max_values=1,
            options=options,
            row=min(chunk_index - 1, 4),
        )

    async def callback(self, interaction: Interaction):
        selected_index = int(self.values[0])
        await interaction.response.send_message(
            **_send_kwargs(self.plan_view.build_detail_components(selected_index=selected_index))
        )


def _format_plan_brief(plan: DiaryPlan) -> str:
    return (
        f"{plan.diaries} 本日記\n"
        f"跳過 {plan.skips} 次\n"
        f"花費 {plan.cost:,} 眾神幣"
    )


def _add_plan_summary_fields(embed: nextcord.Embed, plans: tuple[DiaryPlan, ...]):
    lines = [
        f"{plan.diaries} 本日記：{plan.cost:,} 眾神幣"
        for plan in plans
    ]
    _add_lines_fields(embed, "日記數與花費", lines)


def _add_segment_fields(embed: nextcord.Embed, plan: DiaryPlan, quests: tuple[QuestExp, ...]):
    lines: list[str] = []
    index = 1

    while index <= len(plan.segments):
        segment = plan.segments[index - 1]
        if segment.end_index < segment.start_index:
            index += 1
            continue

        repeat_count = 1
        while index + repeat_count <= len(plan.segments):
            next_segment = plan.segments[index + repeat_count - 1]
            if (
                next_segment.start_index != segment.start_index
                or next_segment.end_index != segment.end_index
                or next_segment.exp != segment.exp
            ):
                break
            repeat_count += 1

        start = quests[segment.start_index]
        end = quests[segment.end_index]
        label = start.label if segment.start_index == segment.end_index else f"{start.label} ~ {end.label}"
        if repeat_count == 1:
            lines.append(f"第 {index} 段\n  {label}，{segment.exp:,} EXP")
        else:
            end_index = index + repeat_count - 1
            lines.append(f"第 {index}-{end_index} 段，重複 {repeat_count} 次\n  {label}，{segment.exp:,} EXP")

        index += repeat_count

    _add_lines_fields(embed, "任務執行範圍", lines or ["無"])


def _add_lines_fields(embed: nextcord.Embed, title: str, lines: list[str], *, max_chars: int = 950):
    if not lines:
        embed.add_field(name=title, value="無", inline=False)
        return

    chunk: list[str] = []
    chunk_length = 0
    field_index = 1

    for line in lines:
        line_length = len(line) + 1
        if chunk and chunk_length + line_length > max_chars:
            field_name = title if field_index == 1 else f"{title} ({field_index})"
            embed.add_field(name=field_name, value="\n".join(chunk), inline=False)
            chunk = []
            chunk_length = 0
            field_index += 1

        chunk.append(line)
        chunk_length += line_length

    if chunk:
        field_name = title if field_index == 1 else f"{title} ({field_index})"
        embed.add_field(name=field_name, value="\n".join(chunk), inline=False)


def _send_kwargs(components: tuple) -> dict:
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

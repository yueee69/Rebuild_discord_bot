import csv
import io
import math
from dataclasses import dataclass
from functools import lru_cache

import requests

from core import constants


@dataclass(frozen=True)
class QuestExp:
    chapter: int
    section: int
    chapter_name: str
    section_name: str
    exp: int

    @property
    def label(self) -> str:
        return f"{self.chapter}.{self.section} {self.section_name}"


@dataclass(frozen=True)
class QuestSegment:
    start_index: int
    end_index: int
    exp: int


@dataclass(frozen=True)
class DiaryPlan:
    diaries: int
    skips: int
    cost: int
    exp: int
    savings_from_previous: int | None
    segments: tuple[QuestSegment, ...]


@dataclass(frozen=True)
class CharacterExpResult:
    required_exp: int
    quest_count: int
    plans: tuple[DiaryPlan, ...]


def get_required_exp(current_level: int) -> int:
    return math.floor(current_level ** 4 / 40) + current_level * 2


def calculate_required_exp(
    current_level: int,
    current_percent: float,
    target_level: int,
    target_percent: float,
) -> int:
    current_total = _total_exp_at(current_level, current_percent)
    target_total = _total_exp_at(target_level, target_percent)
    return max(0, math.ceil(target_total - current_total))


@lru_cache(maxsize=1)
def load_main_quests() -> tuple[QuestExp, ...]:
    response = requests.get(constants.CHARACTER_EXP_QUEST_CSV_URL, timeout=20)
    response.raise_for_status()
    rows = csv.reader(io.StringIO(response.text))

    quests: list[QuestExp] = []
    current_chapter: int | None = None
    current_chapter_name = ""

    for index, row in enumerate(rows):
        if index < 2:
            continue

        row = [*row, "", "", "", "", "", "", "", "", ""]
        chapter_value = row[0].strip()
        if chapter_value.isdigit():
            current_chapter = int(chapter_value)
            current_chapter_name = row[1].strip()

        section_value = row[2].strip()
        exp_value = row[4].replace(",", "").strip()
        special_flag = row[5].strip().lower()

        if current_chapter is None or not section_value.isdigit() or not exp_value.isdigit():
            continue
        if special_flag == "skip":
            continue

        exp = int(exp_value)
        if exp <= 0:
            continue

        quests.append(
            QuestExp(
                chapter=current_chapter,
                section=int(section_value),
                chapter_name=current_chapter_name,
                section_name=row[3].strip(),
                exp=exp,
            )
        )

    return tuple(quests)


def calculate_character_exp_plans(
    current_level: int,
    current_percent: float,
    target_level: int,
    target_percent: float,
    diary_limit: int = constants.CHARACTER_EXP_DIARY_ENUMERATION_LIMIT,
) -> CharacterExpResult:
    _validate_level(current_level)
    _validate_level(target_level)
    _validate_percent(current_percent)
    _validate_percent(target_percent)

    required_exp = calculate_required_exp(current_level, current_percent, target_level, target_percent)
    quests = load_main_quests()
    if required_exp == 0:
        return CharacterExpResult(required_exp=0, quest_count=len(quests), plans=())

    initial_segments = _build_initial_segments(quests)
    best_segments = _build_best_segments(quests)
    plans: list[DiaryPlan] = []
    previous_cost: int | None = None
    best_skips: int | None = None
    theoretical_min_skips = math.ceil(required_exp / max(quest.exp for quest in quests))
    states = _build_initial_states(initial_segments)

    for diaries in range(diary_limit + 1):
        plan = _find_best_plan_in_states(required_exp, diaries, states)
        if plan and (best_skips is None or plan.skips < best_skips):
            savings = None if previous_cost is None else max(0, previous_cost - plan.cost)
            plans.append(
                DiaryPlan(
                    diaries=diaries,
                    skips=plan.skips,
                    cost=plan.cost,
                    exp=plan.exp,
                    savings_from_previous=savings,
                    segments=plan.segments,
                )
            )
            best_skips = plan.skips
            previous_cost = plan.cost

            if plan.skips <= theoretical_min_skips:
                break

        if diaries == diary_limit:
            break

        max_skips = (best_skips - 1) if best_skips is not None else (diaries + 2) * len(quests)
        states = _advance_diary_states(states, best_segments, max_skips=max_skips)

    return CharacterExpResult(
        required_exp=required_exp,
        quest_count=len(quests),
        plans=tuple(plans),
    )


def _total_exp_at(level: int, percent: float) -> float:
    completed_levels = sum(get_required_exp(current_level) for current_level in range(1, level))
    current_level_progress = get_required_exp(level) * (percent / 100)
    return completed_levels + current_level_progress


def _validate_level(level: int):
    if level < 1 or level > constants.CHARACTER_MAX_LEVEL:
        raise ValueError(f"等級必須介於 1 到 {constants.CHARACTER_MAX_LEVEL}。")


def _validate_percent(percent: float):
    if percent < 0 or percent > 100:
        raise ValueError("經驗百分比必須介於 0 到 100。")


def _build_initial_segments(quests: tuple[QuestExp, ...]) -> list[QuestSegment]:
    segments = [QuestSegment(0, -1, 0)]
    total_exp = 0
    for end_index, quest in enumerate(quests):
        total_exp += quest.exp
        segments.append(QuestSegment(0, end_index, total_exp))
    return segments


def _build_best_segments(quests: tuple[QuestExp, ...]) -> list[QuestSegment]:
    best_segments = [QuestSegment(0, -1, 0)]
    for length in range(1, len(quests) + 1):
        window_exp = sum(quest.exp for quest in quests[:length])
        best = QuestSegment(0, length - 1, window_exp)

        for start_index in range(1, len(quests) - length + 1):
            window_exp += quests[start_index + length - 1].exp - quests[start_index - 1].exp
            if window_exp > best.exp:
                best = QuestSegment(start_index, start_index + length - 1, window_exp)

        best_segments.append(best)
    return best_segments


def _build_initial_states(initial_segments: list[QuestSegment]) -> dict[int, tuple[int, tuple[QuestSegment, ...]]]:
    states: dict[int, tuple[int, tuple[QuestSegment, ...]]] = {}
    for skips, segment in enumerate(initial_segments):
        segments = tuple() if skips == 0 else (segment,)
        states[skips] = (segment.exp, segments)
    return _prune_states(states)


def _advance_diary_states(
    states: dict[int, tuple[int, tuple[QuestSegment, ...]]],
    best_segments: list[QuestSegment],
    *,
    max_skips: int,
) -> dict[int, tuple[int, tuple[QuestSegment, ...]]]:
    next_state: dict[int, tuple[int, tuple[QuestSegment, ...]]] = {}

    for used_skips, (used_exp, segments) in states.items():
        for length, segment in enumerate(best_segments):
            total_skips = used_skips + length
            if total_skips > max_skips:
                break

            total_exp = used_exp + segment.exp
            current_best = next_state.get(total_skips)
            if current_best is None or total_exp > current_best[0]:
                next_segments = segments if length == 0 else (*segments, segment)
                next_state[total_skips] = (total_exp, next_segments)

    return _prune_states(next_state)


def _prune_states(
    states: dict[int, tuple[int, tuple[QuestSegment, ...]]]
) -> dict[int, tuple[int, tuple[QuestSegment, ...]]]:
    pruned: dict[int, tuple[int, tuple[QuestSegment, ...]]] = {}
    best_exp = -1

    for skips in sorted(states):
        exp, segments = states[skips]
        if exp <= best_exp:
            continue

        pruned[skips] = (exp, segments)
        best_exp = exp

    return pruned


def _find_best_plan_in_states(
    required_exp: int,
    diaries: int,
    states: dict[int, tuple[int, tuple[QuestSegment, ...]]],
) -> DiaryPlan | None:
    for skips in sorted(states):
        exp, segments = states[skips]
        if exp >= required_exp:
            return DiaryPlan(
                diaries=diaries,
                skips=skips,
                cost=skips * constants.CHARACTER_EXP_QUEST_SKIP_COST,
                exp=exp,
                savings_from_previous=None,
                segments=segments,
            )

    return None

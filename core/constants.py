import json
import os
from pathlib import Path

# ======== variables =========
TIME_ZONE = 8  # UTC+8

# ======== character settings =========
CHARACTER_MAX_LEVEL = 325
CHARACTER_EXP_QUEST_SKIP_COST = 500_000
CHARACTER_EXP_DIARY_ENUMERATION_LIMIT = 20
CHARACTER_EXP_QUEST_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1hh66cAWlDk2uJlAbv2ivdrRNQYuK4RPuWF4iB48T31g/pub"
    "?gid=1111992028&single=true&output=csv&range=A:I"
)

# ======== coin activity settings =========
USER_LEVEL_COIN_UNIT = 1500
FORTUNE_COIN_PRICE = 3500
DISPLAY_TEN_THOUSAND_UNIT = 10000

MESSAGE_COIN_PER_CHARACTER = 1
VOICE_COIN_PER_CHECK = 30
STREAM_COIN_PER_CHECK = 50
DAILY_VOICE_COIN_LIMIT = 3000
DAILY_STREAM_COIN_LIMIT = 5000
VOICE_REWARD_CHECK_INTERVAL_SECONDS = 60
DAILY_EVENT_CHECK_INTERVAL_SECONDS = 60

# ======== daily shop settings =========
DAILY_SHOP_DISABLED_VISIBLE_ITEM_KEYWORDS = ("RPG金幣", "RPG 金幣")
DAILY_SHOP_RANDOM_GOODS_COUNT = 3
DAILY_SHOP_LEFT_COUNT_MIN = 1
DAILY_SHOP_LEFT_COUNT_MAX = 7
DAILY_SHOP_DEFAULT_ITEMS = (
    ("3陽壽", FORTUNE_COIN_PRICE * 3, 35, 42),
    ("5陽壽", FORTUNE_COIN_PRICE * 5, 35, 18),
    ("7陽壽", FORTUNE_COIN_PRICE * 7, 40, 12),
    ("10陽壽", FORTUNE_COIN_PRICE * 10, 50, 5),
    ("5萬眾神幣", 5000, 5, 10),
    ("10萬眾神幣", 10000, 10, 5),
    ("50萬眾神幣", 45000, 100, 5),
    ("100萬眾神幣", 60000, 100, 1),
    ("舞者之書", 80000, 50, 1),
    ("魔法戰士之書", 70000, 50, 1),
)

# ======== lottery settings =========
NORM_LOTTERY_PRICE_PER_DRAW = 1
NORM_LOTTERY_MIN_DRAWS = 1
NORM_LOTTERY_MAX_DRAWS = 25
ITEM_LOTTERY_PRICE_PER_DRAW = 5
ITEM_LOTTERY_DRAW_COUNT = 10
XTAL_LOTTERY_PRICE_PER_DRAW = 5
XTAL_LOTTERY_MIN_DRAWS = 1
XTAL_LOTTERY_MAX_DRAWS = 25

# ======== lavalink settings =========
BASE_DIR = Path(__file__).resolve().parent.parent
LAVALINK_NODES_FILE = BASE_DIR / "Json" / "lavalink_nodes.json"


def _load_lavalink_nodes() -> list[dict]:
    with LAVALINK_NODES_FILE.open("r", encoding="utf-8") as file:
        nodes = json.load(file)

    if not isinstance(nodes, list) or not nodes:
        raise RuntimeError(f"{LAVALINK_NODES_FILE} must contain at least one Lavalink node.")

    return nodes


LAVALINK_NODES = _load_lavalink_nodes()
LAVALINK_LABELS = tuple(node["name"] for node in LAVALINK_NODES)

DO_NOT_ROLE = [
    "頭等鮭魚腹",
    "次等鮭魚腹",
    "鮭魚幹部",
    "食物鏈頂端",
    "花椰菜",
    "狗子",
    "鮭魚卵",
    "鮭魚們",
    "會外鮭魚",
    "會內鮭魚",
    "鮭姬",
    "鮭魚乾爹"
    ]

ENABLE_COMMAND_USE_GUILDS = [
    972795227779772418,
    988729128121430036
]

# ======== strings =========
STR_MUSIC_HELP = \
"""
音樂機器人快速上手

1. 你先加入語音房。
2. 使用 /播放 連結 貼上 YouTube 或 Spotify 單曲/歌單連結。
3. 機器人會自動加入你的語音房，並建立控制面板。
4. 後續再用 /播放 會加入佇列。

常用指令：
- /播放：播放單曲或加入歌單到佇列
- /加入語音：讓機器人先加入你的語音房
- /音樂面板：重新叫出目前播放控制板
- /音量：直接設定 0-100 音量
- /離開語音：停止播放、清空狀態並離開語音房

控制面板：
- 暫停 / 繼續
- 下一首
- 切換播放模式：普通播放、單曲循環、隨機播放
- 查看佇列與歷史紀錄
- 調整音量
- 停止並離開語音房

佇列功能：
- 翻頁查看全部歌曲
- 批量移除當前頁面的歌曲
- 清空佇列
- 跳到指定歌曲

權限限制：
控制面板、音量、佇列、離開等操作，只允許和機器人在同一個語音房的人使用。
"""

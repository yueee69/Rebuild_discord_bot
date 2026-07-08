# ======== variables =========
TIME_ZONE = 8  # UTC+8

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
指令前綴& 如果指令是中文，則簡體繁體都有效

# &j &jo (join) &加入語音
>加入目前用戶所在語音房

# &l &le (leave) &退出語音
>退出目前用戶的語音房

# &p &pl (play) &播放
## ⭡播歌用這個！！！
>此指令必須在後面跟上連結或是搜尋歌名

目前只支援：
- yt單曲、歌單
- mixerbox歌單
- Spotify完全不支援
搜尋名稱有時候會不準確 建議打語歌曲相關的名稱

# &skip (skip) &跳過
>跳過這首歌 如果後面沒歌了就會直接結束

# &s &st (stop) &暫停
>暫停這首歌

# &r &re (resume) &繼續
>繼續暫停的歌

# &list (list) &佇列
>顯示目前正在排隊的歌(不包含當前播放的歌)

# &i (infomation) &訊息 &歌曲訊息
>顯示當前撥放歌曲的詳細訊息、以及大部分功能按鈕化(控制面板)

# 控制面板(用&i會跳出來)
以下有一些指令沒有的功能：

## -播放狀態：
    共有三種狀態：
    -普通輪播
    -單首循環
    -隨機撥放  
    預設是普通輪播，每按一次會切換到下一種狀態。

## -最愛清單：
    允許你珍藏喜歡的歌，以便你快速搜尋，加入歌單(上限25首)
    ※**只限定單曲，歌單暫不支援，有需要再做**

## -歷史紀錄
    列出上五首播的歌，以便你不知道聽了啥。

## -調整音量
    可以調整0~100 0為靜音，100為最大聲。

打算做但還沒做：
1.批量跳過(斟酌中)

注意事項：
1.整體使用體驗不如專業的音樂機器人(Ex.很多bug、使用不順) 意在中文化使用
2.有任何建議(或bug)歡迎提出
"""




from enum import Enum

class AutoBuy_Plan(Enum):
    # 自動買入計畫
    NONE = 0  # 不啟用
    HIGHEST_LIFESPAN = 1  # 最高陽壽方案
    BEST_COST_PERFORMANCE = 2  # CP值最高方案
from dataclasses import dataclass
from new_bot.models.trusteeship.enums.buy_type import AutoBuy_Plan
from new_bot.models.trusteeship.enums.feature_type import FeatureType
from new_bot.models.trusteeship.basePlan import DailyTrusteeshipPlan

@dataclass
class GoldPlan(DailyTrusteeshipPlan):
    def __init__(self, remaining_days: int = 0, purchase_days: int = 0, notice: bool = False, buy_plan: AutoBuy_Plan = AutoBuy_Plan.NONE):
        name = "gold"
        description = "黃金套餐 (自動**購買每日商品** | 自動**抽獎**)"
        features = [FeatureType.AUTO_BUY, FeatureType.AUTO_LOTTERY]
        super().__init__(name, remaining_days, purchase_days, notice, buy_plan, description, features)

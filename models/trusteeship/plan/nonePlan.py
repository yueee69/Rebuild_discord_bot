from dataclasses import dataclass
from new_bot.models.trusteeship.enums.buy_type import AutoBuy_Plan
from new_bot.models.trusteeship.basePlan import DailyTrusteeshipPlan

@dataclass
class NonePlan(DailyTrusteeshipPlan):
    def __init__(self, *args, **kwargs):
        name = "none"
        description = "無套餐"
        super().__init__(name, 0, 0, False, AutoBuy_Plan.NONE, description, None)

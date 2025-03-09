from new_bot.models.trusteeship.plan.diamondPlan import DiamondPlan
from new_bot.models.trusteeship.plan.goldPlan import GoldPlan
from new_bot.models.trusteeship.plan.platinumPlan import PlatinumPlan
from new_bot.models.trusteeship.plan.nonePlan import NonePlan
from new_bot.models.trusteeship.basePlan import DailyTrusteeshipPlan
from new_bot.models.trusteeship.enums.buy_type import AutoBuy_Plan

class PlanFactory:
    _plans = {
        "diamond": DiamondPlan,
        "gold": GoldPlan,
        "platinum": PlatinumPlan,
        "none": NonePlan
    }

    @staticmethod
    def create(plan_name: str, remaining_days: int = 0, purchase_days: int = 0, notice: bool = False, buy_plan: AutoBuy_Plan = AutoBuy_Plan.NONE) -> DailyTrusteeshipPlan:
        """根據 plan_name 建立對應的方案物件"""
        plan_class = PlanFactory._plans.get(plan_name.lower(), NonePlan)  # 預設為無方案
        if isinstance(buy_plan, str):
            # AutoBuy_Plan[buy_plan.upper()] or AutoBuy_Plan.NONE
            buy_plan = AutoBuy_Plan[buy_plan.upper()] if buy_plan.upper() in AutoBuy_Plan.__members__ else AutoBuy_Plan.NONE
        
        return plan_class(remaining_days, purchase_days, notice, buy_plan)

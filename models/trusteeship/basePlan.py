from dataclasses import dataclass
from new_bot.models.trusteeship.enums.feature_type import FeatureType
from new_bot.models.trusteeship.enums.buy_type import AutoBuy_Plan

@dataclass
class DailyTrusteeshipPlan:
    remaining_days: int
    purchase_days: int
    notice: bool
    buy_plan: AutoBuy_Plan
    name: str
    description: str 
    features: list[FeatureType] = None
    
    def __init__(self, name: str, remaining_days: int, purchase_days: int, notice: bool, buy_plan: AutoBuy_Plan, description: str, features: list[FeatureType] = None):
        self._name = name # name of the plan
        self._description = description # description of the plan
        self.remaining_days = (remaining_days if remaining_days > 0 else 0) # remaining days of the plan
        self.purchase_days = (purchase_days if purchase_days > 0 else 0)
        self.notice = notice
        self.buy_plan = (buy_plan if buy_plan is not None else AutoBuy_Plan.NONE)
        self._features = features if features is not None else []
        
    def excute(self):
        for feature in self.features:
            feature.value.excute()
        
    @property
    def name(self):
        return self._name
    
    @property
    def description(self):
        return self._description
    
    @property
    def features(self):
        return self._features
    
    
    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'remaining_days': self.remaining_days,
            'purchase_days': self.purchase_days,
            'notice': self.notice,
            'buy_plan': self.buy_plan.name
        }
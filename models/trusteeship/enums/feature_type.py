# FeatureType (如果用來存套餐的功能)
from enum import Enum, auto
from new_bot.features.auto_buy_feature import AutoBuyFeature
from new_bot.features.auto_lottery_feature import AutoLotteryFeature
from new_bot.features.auto_sign_in_feature import AutoSignInFeature

class FeatureType(Enum):
    AUTO_BUY = AutoBuyFeature()
    AUTO_LOTTERY = AutoLotteryFeature()
    AUTO_SIGN_IN = AutoSignInFeature()
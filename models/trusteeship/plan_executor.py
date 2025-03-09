from new_bot.models.trusteeship.basePlan import DailyTrusteeshipPlan
from new_bot.models.user_manager import User
from new_bot.models.trusteeship.enums.feature_type import FeatureType

class PlanExecutor:
    @staticmethod
    def execute(plan: DailyTrusteeshipPlan, user: User):
        for features in plan.features:
            features = FeatureType(features)
            
            match features:
                case FeatureType.AUTO_BUY:
                    features.value.execute()
                case FeatureType.AUTO_LOTTERY:
                    features.value.execute()
                case FeatureType.AUTO_SIGN_IN:
                    features.value.execute()
                
        
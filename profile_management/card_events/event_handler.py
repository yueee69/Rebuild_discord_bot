import random

from .actor import Actor, ActorPair
from profile_management.card_events import event

class Handler:
    ACTIVE_RATE = 100

    def __init__(self, context: object):
        user_actor = Actor(context.user_item, context.interaction.user)
        target_actor = Actor(context.target_item, context.target_user)
        self.pair = ActorPair(user_actor, target_actor)
        self.context = context

    def __random_active(self) -> bool:
        return random.randint(1, 100) <= self.ACTIVE_RATE
    
    def __condition_detect(self) -> bool:
        return (
            self.__random_active() #是否觸發
            and self.context.target_item.protect #是否開啟迴轉
            and (self.context.user.id != self.context.target_user.id) #target是否是自己
        )

    def main(self) -> None:
        if self.__condition_detect():
            self.context.target_item.trans_card -= 1
            event.EventChoice.main(self.context, self.pair)
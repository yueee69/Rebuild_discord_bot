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

    def random_active(self) -> bool:
        return random.randint(1, 100) <= self.ACTIVE_RATE

    def main(self) -> None:
        if self.random_active() and self.context.target_item.protect:
            self.context.target_item.trans_card -= 1
            event.EventChoice.main(self.context, self.pair)
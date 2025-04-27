from dataclasses import dataclass
from models.item_manager import Item_data

@dataclass
class Actor:
    item: Item_data
    user: object

@dataclass
class ActorPair:
    actor1: Actor
    actor2: Actor

    def get_other(self, actor: Actor) -> Actor:
        return self.actor2 if actor is self.actor1 else self.actor1

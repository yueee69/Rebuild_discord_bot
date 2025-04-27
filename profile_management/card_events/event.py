from abc import ABC, abstractmethod

from .actor import ActorPair
from views.item_crad_check_view import Create

import random
import asyncio
import nextcord

class BaseEvent(ABC):
    name: str

    @abstractmethod
    def apply(self, context: object, actor_pair: ActorPair):
        pass


class StealCard(BaseEvent):
    name = "偷卡片"

    def apply(self, context: object, actor_pair: ActorPair):
        actor = random.choice([actor_pair.actor1, actor_pair.actor2])
        other = actor_pair.get_other(actor)

        eng_card, chinese_card = actor.item.random_card() #隨機一張卡
        count = random.randint(1, 5) #隨機偷1~5張卡
        deduct = min(getattr(actor.item, eng_card), count) #實際可以扣除的數量 有可能玩家卡不足

        setattr(actor.item, eng_card, getattr(actor.item, eng_card) - deduct)
        setattr(other.item, eng_card, getattr(other.item, eng_card) + deduct)

        context.event_message += f"\n{other.user.display_name} 偷了 {actor.user.display_name} {deduct} 張 {chinese_card}！"


class ClearCard(BaseEvent):
    name = "清空卡片"

    def apply(self, context: object, actor_pair: ActorPair):
        actor = random.choice([actor_pair.actor1, actor_pair.actor2])
        eng_card, chinese_card = actor.item.random_card() #隨機一張卡

        clear_count = getattr(actor.item, eng_card)
        setattr(actor.item, eng_card, 0) #直接設為0

        context.event_message += f"{actor.user.display_name} 的 {clear_count} 張 {chinese_card} 被清空了！"


class ExtraDeduct(BaseEvent):
    name = "額外卡片扣除懲罰"

    def apply(self, context: object, actor_pair: ActorPair):
        actor = random.choice([actor_pair.actor1, actor_pair.actor2])
        eng_card, chinese_card = actor.item.random_card() #隨機一張卡

        percent = random.uniform(0.05, 0.5) #5%~50%的幅度
        deduct_count = int(getattr(actor.item, eng_card) * percent)
        setattr(actor.item, eng_card, getattr(actor.item, eng_card) - deduct_count)

        context.event_message += f"\n{actor.user.display_name} 被額外扣除了 `{int(percent * 100)}%`({deduct_count}) 的 {chinese_card}！"


class ExchangeCard(BaseEvent):
    name = "交易"
    EXTRA_EVENT_PERCENT = 10

    def apply(self, context: object, actor_pair: ActorPair):
        actor = random.choice([actor_pair.actor1, actor_pair.actor2])
        other = actor_pair.get_other(actor)

        eng_card, chinese_card = actor.item.random_card() #隨機一張卡
        tmp = getattr(actor.item, eng_card)
        setattr(actor.item, eng_card, getattr(other.item, eng_card))
        setattr(other.item, eng_card, tmp)

        context.event_message += f"\n{actor.user.display_name} 和 {other.user.display_name} 交換了 {chinese_card}！" #不對外公開數量
        if random.randint(1, 100) <= self.EXTRA_EVENT_PERCENT:
            doing = ["在發呆", "爛網", "手滑"]
            context.event_message += f"\n但因為機器人{random.choice(doing)}，觸發了額外懲罰"
            ExtraDeduct().apply(context, actor_pair)

class EventCancel(BaseEvent):
    name = "取消事件"

    def apply(self, context: object, actor_pair: ActorPair):
        context.event_cancel = True
        context.event_message += "\n迴轉卡取消了這次事件！"

class LookingOtherCard(BaseEvent):
    name = "窺探"

    def apply(self, context: object, actor_pair: ActorPair):
        actor = random.choice([actor_pair.actor1, actor_pair.actor2])
        other = actor_pair.get_other(actor)

        embed, *_ = Create.get_components(actor)
        try:
            asyncio.create_task(other.user.send(embed=embed))

        except nextcord.Forbidden:
            context.event_message = f"❌ 無法私訊 {other.user.display_name}"
            return
        context.event_message += f"\n{other.user.display_name} 窺探了 {actor.user.display_name} 的道具卡！"

class EventChoice:
    EVENTS = [
        (StealCard, 20), (ClearCard, 5), (ExtraDeduct, 15), (ExchangeCard, 10), (EventCancel, 50),
        (LookingOtherCard, 1000)
        ]

    @staticmethod
    def main(context: object, actor_pair: ActorPair) -> None:
        event_classes, weights = zip(*EventChoice.EVENTS)
        select = random.choices(event_classes, weights = weights, k = 1)[0]  # 抽出一個事件class

        event = select()
        context.event_message = f"觸發事件: {event.name}，"
        event.apply(context, actor_pair)
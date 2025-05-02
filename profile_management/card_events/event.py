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
    name = "《黒の掌握》"

    def apply(self, context: object, actor_pair: ActorPair):
        actor = random.choice([actor_pair.actor1, actor_pair.actor2])
        other = actor_pair.get_other(actor)

        eng_card, chinese_card = actor.item.random_card() #隨機一張卡
        count = random.randint(1, 5) #隨機偷1~5張卡
        deduct = min(getattr(actor.item, eng_card), count) #實際可以扣除的數量 有可能玩家卡不足

        setattr(actor.item, eng_card, getattr(actor.item, eng_card) - deduct)
        setattr(other.item, eng_card, getattr(other.item, eng_card) + deduct)

        context.event_message += (
            f"\n【{other.user.mention}】悄然出手，使出{self.name}，\n"
            f"從【{actor.user.mention}】的記憶裂縫中竊取了 {deduct} 張【{chinese_card}】……"
        )


class ClearCard(BaseEvent):
    name = "《零界斷罪》"

    def apply(self, context: object, actor_pair: ActorPair):
        actor = random.choice([actor_pair.actor1, actor_pair.actor2])
        eng_card, chinese_card = actor.item.random_card() #隨機一張卡

        clear_count = getattr(actor.item, eng_card)
        setattr(actor.item, eng_card, 0) #直接設為0

        context.event_message += (
            f"\n時間凝結，命運審判。\n【{actor.user.mention}】的 {clear_count} 張【{chinese_card}】被{self.name}吞噬，化為虛無。"
        )


class ExtraDeduct(BaseEvent):
    name = "《業火焚身》"

    def apply(self, context: object, actor_pair: ActorPair):
        actor = random.choice([actor_pair.actor1, actor_pair.actor2])
        eng_card, chinese_card = actor.item.random_card() #隨機一張卡

        percent = random.uniform(0.05, 0.5) #5%~50%的幅度
        deduct_count = int(getattr(actor.item, eng_card) * percent)
        setattr(actor.item, eng_card, getattr(actor.item, eng_card) - deduct_count)

        context.event_message += (
            f"\n審判之炎，已降臨於罪者之身，\n"
            f"{actor.user.mention} 失去了 `{int(percent * 100)}%`({deduct_count}) 的 {chinese_card}！"
            )


class ExchangeCard(BaseEvent):
    name = "《Re:Link — 連鎖誤差》"
    EXTRA_EVENT_PERCENT = 25

    def apply(self, context: object, actor_pair: ActorPair):
        actor = random.choice([actor_pair.actor1, actor_pair.actor2])
        other = actor_pair.get_other(actor)

        eng_card, chinese_card = actor.item.random_card() #隨機一張卡
        tmp = getattr(actor.item, eng_card)
        setattr(actor.item, eng_card, getattr(other.item, eng_card))
        setattr(other.item, eng_card, tmp)

        context.event_message += (
            f"\n【{actor.user.mention}】與【{other.user.mention}】被命運之環所困，\n"
            f"交換了未知的能量碎片：{chinese_card}。"
        )
        if random.randint(1, 100) <= self.EXTRA_EVENT_PERCENT:
            doing = ["在發呆", "爛網", "手滑"]
            context.event_message += f"\n但因為機器人{random.choice(doing)}，觸發了額外懲罰"
            ExtraDeduct().apply(context, actor_pair)

class EventCancel(BaseEvent):
    name = "《絕對否決》"

    def apply(self, context: object, actor_pair: ActorPair):
        context.event_cancel = True
        context.event_message += f"\n 空間逆轉 —— 事件被{self.name}所抹消，命運暫停！"

class LookingOtherCard(BaseEvent):
    name = "《窥視者の眼》"

    def apply(self, context: object, actor_pair: ActorPair):
        actor = random.choice([actor_pair.actor1, actor_pair.actor2])
        other = actor_pair.get_other(actor)

        random_display_count = random.randint(1, 4) #隨機1~4筆資訊
        card_index = random.sample([0, 1, 2, 3, 4], k = random_display_count)

        embed, *_ = Create.get_components(interaction = actor, info_index = card_index)
        try:
            asyncio.create_task(other.user.send(embed = embed))

        except nextcord.Forbidden:
            context.event_message = f"❌ 無法私訊 {other.user.mention}"
            return
        context.event_message += (
            f"\n【{actor.user.mention}】啟動 {self.name}，潛入【{other.user.mention}】的記憶，\n"
            f"探知了 {random_display_count} 種神秘卡片的真相。"
        )

class EventChoice:
    EVENTS = [
        (StealCard, 20), (ClearCard, 5), (ExtraDeduct, 15), (ExchangeCard, 15), (EventCancel, 30),
        (LookingOtherCard, 15)
        ]

    @staticmethod
    def main(context: object, actor_pair: ActorPair) -> None:
        event_classes, weights = zip(*EventChoice.EVENTS)
        select = random.choices(event_classes, weights = weights, k = 1)[0]  # 抽出一個事件class

        event = select()
        context.event_message = f"✨ 星辰變幻，天象異動，觸發異象\n—— **{event.name}**"
        event.apply(context, actor_pair)
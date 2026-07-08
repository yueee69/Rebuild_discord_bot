"""
這裡用於計算各種購買的消耗
"""
from core import constants


class Calculater:
    @staticmethod
    def exchange_fortune(user_object: object, fortune: int):
        user_data = user_object.user
        user_data.coin -= fortune * constants.FORTUNE_COIN_PRICE
        user_data.fortune += fortune
        user_object.save_all_users()

    @staticmethod
    def daily_shop_buy(user_object: object, coin: int):
        user_data = user_object.user
        user_data.coin -= coin

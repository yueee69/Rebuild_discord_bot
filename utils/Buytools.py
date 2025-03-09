"""
這裡用於計算各種購買的消耗
"""

class Calculater:
    @staticmethod
    def exchange_fortune(user_object: object, fortune: int):
        user_data = user_object.user
        user_data.coin -= fortune * 3500
        user_data.fortune += fortune
        user_object.save_all_users()
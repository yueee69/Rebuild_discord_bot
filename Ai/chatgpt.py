import openai

import os
from dotenv import load_dotenv

class Tool:
    def __init__(self):  
        load_dotenv()
        self.client = openai.OpenAI(api_key = os.environ.get("CHATGPT_KEY"))
        self.AI_VERSION = "gpt-4o-mini"

    def ask(self, system_info: str, question: str, max_token: int = 1000, temp: float = 0.7):
        """
        prarms:
            system_info: 給Ai的預設訊息(例如人設、前提)
            question: 真正要詢問的訊息
            max_token: 限制Ai回傳訊息的長度
            temp: 控制Ai情緒的溫度值:
                0.0	回應更嚴謹、可預測，適合數據處理
                0.7	適度創意、標準對話（推薦）
                1.2	非常創意，可能會產生有趣但奇怪的答案
        """
        if not (system_info and question): #處理兩個資訊都空的情況 省錢
            return

        response = self.client.chat.completions.create(
            model = self.AI_VERSION,
            messages=[
                {"role": "system", "content": system_info},
                {"role": "user", "content": question},
            ],
            max_tokens = max_token,
            temperature = temp
        )
        
        return response.choices[0].message.content.strip()

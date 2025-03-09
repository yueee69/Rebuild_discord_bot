from nextcord import Interaction, TextInputStyle
from nextcord.ui import Modal, TextInput

class GenericModal(Modal):
    """
    通用 Modal 類別，可以動態加入多個 TextInput 欄位，
    並在提交後呼叫自訂的 callback 處理輸入資料。
    
    :param title: Modal 的標題。
    :param input_fields: 一個欄位配置列表，每個欄位用 dict 定義。
    :param custom_callback: 自訂的 callback 函數，會在 on_submit 裡被呼叫，
    """
    def __init__(self, title: str, input_fields: list, custom_callback) -> Modal:
        super().__init__(title=title)
        self.inputs = {}  # 儲存每個欄位的物件
        self.custom_callback = custom_callback

        for field in input_fields:
            text_input = TextInput(
                label=field.get("label"),
                placeholder=field.get("placeholder", ""),
                required=field.get("required", True),
                style=field.get("style", TextInputStyle.short)
            )
            self.add_item(text_input)
            key = field.get("name", field.get("label"))
            self.inputs[key] = text_input

        self.callback = self.on_submit

    async def on_submit(self, interaction: Interaction):
        # 收集所有輸入欄位的資料
        responses = { key: item.value for key, item in self.inputs.items() }
        await self.custom_callback(interaction, responses)

from views import pay_view
from managers.user_manager import UserManager
from features.coin import coin_manager

from nextcord import Interaction, User, NotFound


class InputCheck:
    def __init__(self, input: object):
        self.input = input

    def check(self):
        if not self.input.user and not self.input.user_name:
            return pay_view.CkeckInputView.need_input()

        if self.input.user and self.input.user_name:
            return pay_view.Error.error(due="請在「成員」和「用戶名」中擇一填寫。")

        if self.input.user:
            self.input.selected_user = self.input.user
            if self.input.selected_user.bot:
                return pay_view.Error.error(due="不可以轉帳給機器人。")
            if self.input.selected_user.id == self.input.interaction.user.id:
                return pay_view.Error.error(due="不可以轉帳給自己。")
            return pay_view.CkeckInputView.main_page(self.input.interaction, self.input.selected_user)

        user_data = FindUserTool(self.input).find_user()
        if len(user_data) == 0:
            return pay_view.CkeckInputView.input_not_found()

        return pay_view.CkeckInputView.select_user(user_data, self.input.interaction)


class Callback:
    def __init__(self, interaction: Interaction):
        self.interaction = interaction
        self.bot = interaction.client

    async def user_select_handle(self):
        user_id = self.interaction.data["values"][0]
        selected_user = await self._resolve_user(user_id)
        embed, view, ephemeral, content = pay_view.CkeckInputView.main_page(self.interaction, selected_user)

        await self.interaction.response.edit_message(
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )

    async def coin_type_choice_handle(self):
        _, coin_id, selected_user_id = self.interaction.data["custom_id"].split("|", 2)
        selected_user = await self._resolve_user(selected_user_id)

        if not self._coin_is_available(coin_id):
            await self.interaction.response.edit_message(
                embed=pay_view.Error.error(due="這個幣種目前沒有開放轉帳。")[0],
                view=None
            )
            return

        embed, view, ephemeral, content, file = pay_view.InputPageView.input_page(
            selected_user,
            coin_id,
            self.interaction
        )

        await self.interaction.response.edit_message(
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {}),
            **({"file": file} if file else {})
        )

    async def send_input_data_modal(self):
        custom_id = self.interaction.data["custom_id"]
        modal = pay_view.BuildView.input_data_modal(custom_id)
        await self.interaction.response.send_modal(modal)

    async def input_data_handle(
        self,
        amount: str,
        input_password: str,
        original_password: str,
        selected_user_id: str,
        coin_id: str
    ):
        selected_user = await self._resolve_user(selected_user_id)
        coin_name = coin_manager.CoinManager(coin_id, self.interaction.user.id).get_coin_name()

        if input_password != original_password:
            await self._fail("驗證碼錯誤，請重新確認圖片中的文字。", selected_user, coin_id)
            return

        try:
            amount = int(amount.strip().replace(",", ""))
        except ValueError:
            await self._fail("金額格式錯誤，請輸入正整數。", selected_user, coin_id)
            return

        if amount <= 0:
            await self._fail("轉帳金額必須大於 0。", selected_user, coin_id)
            return

        if selected_user.id == self.interaction.user.id:
            await self._fail("不可以轉帳給自己。", selected_user, coin_id)
            return

        if selected_user.bot:
            await self._fail("不可以轉帳給機器人。", selected_user, coin_id)
            return

        if not self._coin_is_available(coin_id):
            await self._fail("這個幣種目前沒有開放轉帳。", selected_user, coin_id)
            return

        sender, sender_status = UserManager().get_user(self.interaction.user.id)
        if not sender:
            await self._fail("你尚未完成登記，無法使用轉帳。", selected_user, coin_id)
            return

        receiver, _ = UserManager().get_user(selected_user.id, from_register=True)

        if coin_id == "salmon_coin":
            if sender.coin < amount:
                await self._fail(
                    f"你的{coin_name}不足，還差 {amount - sender.coin:,}。",
                    selected_user,
                    coin_id
                )
                return

            sender.coin -= amount
            receiver.coin += amount
        else:
            await self._fail("這個幣種目前沒有開放轉帳。", selected_user, coin_id)
            return

        embed, view, ephemeral, content = pay_view.InputPageView.success_page(
            self.interaction,
            selected_user,
            coin_name,
            amount,
            sender.coin
        )
        await self.interaction.response.edit_message(
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {}),
            attachments=[],
        )

    async def _fail(self, message: str, selected_user: User, coin_id: str):
        embed, view, ephemeral, content, file = pay_view.InputPageView.input_page(
            selected_user,
            coin_id,
            self.interaction
        )

        await self.interaction.response.edit_message(
            embed=embed,
            view=view,
            content=f":x: {message}",
            file=file
        )

    async def _resolve_user(self, user_id: str | int) -> User:
        user = self.bot.get_user(int(user_id))
        if user:
            return user
        return await self.bot.fetch_user(int(user_id))

    def _coin_is_available(self, coin_id: str) -> bool:
        manager = coin_manager.CoinManager(coin_id, self.interaction.user.id)
        return bool(manager.get_coin_name()) and manager.find_user_in_data()


class FindUserTool:
    def __init__(self, input: object):
        self.input = input

    def find_user(self) -> list[User]:
        found = []
        query = self.input.user_name.lower()
        user_data = self.load_user_names()
        for user in user_data:
            names = [
                getattr(user, "name", "") or "",
                getattr(user, "global_name", "") or "",
                getattr(user, "display_name", "") or "",
            ]
            if any(query in name.lower() for name in names) and not user.bot:
                found.append(user)

        return found[:25]

    def load_user_names(self) -> list[User]:
        user_data: list[User] = []
        manager_data = list(UserManager().UserDatas.values())
        for info in manager_data:
            try:
                user = self.input.interaction.client.get_user(int(info.user_id))
                if user:
                    user_data.append(user)
            except NotFound:
                continue

        return user_data

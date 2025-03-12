import nextcord
from nextcord import Interaction
from utils.general import Toolkit
from views.BASIC_VIEW import BASIC_VIEW

class BaseRanking():
    def __init__(self, interaction: Interaction, manager, display_attr: str, thumbnail: str = None, title: str = "", MAX_DISPLAY: int = 5):
        self.MAX_DISPLAY = MAX_DISPLAY
        self.interaction = interaction
        self.manager = manager  # 傳入 Manager
        self.display_attr = display_attr
        self.thumbnail = thumbnail
        self.title = title
        
        self.data_list, self.user = self.get_sorted_list()

    def get_sorted_list(self):
        """統一排行榜資料獲取與排序"""
        user = self.manager.get_user(self.interaction.user.id) if hasattr(self.manager, "get_user") else None
        user_data_dict = self.get_user_data_dict()

        if not user_data_dict:  # 防止 UserDatas 為 None
            return [], user

        sorted_list = sorted(
            user_data_dict.items(),
            key=lambda item: getattr(item[1], self.display_attr, 0),  # 避免 display_attr 不存在時報錯
            reverse=True
        )
        return sorted_list, user

    def get_user_data_dict(self):
        """動態獲取 Manager 內的數據字典"""
        for attr_name in dir(self.manager):
            attr_value = getattr(self.manager, attr_name, None)
            if isinstance(attr_value, dict):  # 找到 dict 就返回
                return attr_value
        return {}  # 如果 Manager 內沒有 dict，返回空字典

    def get_components(self):
        return self.file_list() if self.data_list else self.No_file()

    def No_file(self) -> BASIC_VIEW:
        embed = nextcord.Embed(
            title = "排行榜",
            description = "- 無排名資訊 -",
            color=Toolkit.randomcolor()
        )
        return BASIC_VIEW.views(embed=embed)

    def file_list(self) -> BASIC_VIEW:
        top_users = [
            (user_id, data) for user_id, data in self.data_list
            if self.interaction.guild.get_member(int(user_id))
        ][:self.MAX_DISPLAY]
        
        user_rank = self.get_user_rank(top_users, self.interaction.user.id)

        embed = nextcord.Embed(
            title = f"{self.title}排行榜",
            description = f"{self.interaction.user.mention} 你的排行位於 [ **#{user_rank}** ]",
            color = Toolkit.randomcolor()
        )

        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)

        for user_id, data in top_users:
            member = self.interaction.guild.get_member(int(user_id))
            if member:
                embed.add_field(
                    name=f"{member.display_name}",
                    value=f"{getattr(data, self.display_attr, 0):,}",  # 避免 None 或不存在的 key 報錯
                    inline=False
                )
        return BASIC_VIEW.views(embed=embed)

    @staticmethod
    def get_user_rank(sorted_list, user_id):
        """找出特定用戶的排名"""
        for rank, (uid, _) in enumerate(sorted_list, start=1):
            if uid == str(user_id):
                return rank
        return "無排名"
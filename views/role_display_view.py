from nextcord import Interaction

from .BASIC_VIEW import BASIC_VIEW
from .PAGE_EMBED_CREATER import get_paginated_embed

class Create:
    @staticmethod
    def get_components(roles: list[dict], interaction: Interaction) -> BASIC_VIEW:
        return get_paginated_embed(
            roles, 
            title = "身分組列表", 
            description = "*中文翻譯可能有些許偏差", 
            interaction = interaction,
            prevent_stealing = True
            )
from nextcord import Interaction

from .drivers.nick_driver import Nick
from .drivers import create_role_driver
from .drivers import role_driver

from dataclasses import dataclass

from models.item_manager import Item_data, ItemManager

@dataclass
class NickContext:
    interaction: Interaction
    user_item: Item_data
    target_user : object
    nick_name: str
    create_role: str
    add_role: str

class Driver:
    def __init__(self):
        self.maps = {
            "nick": Nick.driver
        }

    async def get(self, interaction: Interaction, service: str, target_user: object = None, 
            nick_name: str = None, create_role: str = None, add_role: str = None):
        context = NickContext(
            interaction = interaction,
            user_item = ItemManager().get_user(interaction.user.id),
            target_user = target_user,
            nick_name = nick_name,
            create_role = create_role,
            add_role = add_role
        )
        return await self.maps.get(service)(context)
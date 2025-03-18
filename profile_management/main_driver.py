from nextcord import Interaction

from .drivers.nick_driver import Nick
from .drivers.create_role_driver import Create_role
from .drivers.assign_role_driver import Assign_role

from dataclasses import dataclass

from models.item_manager import Item_data, ItemManager

@dataclass
class Context:
    interaction: Interaction
    user_item: Item_data
    target_user : object
    nick_name: str
    create_role_name: str
    create_role_color: str
    created_role: object
    add_role: object
    
class Driver:
    def __init__(self):
        self.maps = {
            "nick": Nick.driver,
            "create_role": Create_role.driver,
            "assign_role": Assign_role.driver
        }

    async def get(self, interaction: Interaction, service: str, target_user: object = None, 
            nick_name: str = None, create_role_name: str = None, create_role_color: str = None,
            add_role: str = None):
              
        context = Context(
            interaction = interaction,
            user_item = ItemManager().get_user(interaction.user.id),
            target_user = target_user,
            nick_name = nick_name,
            create_role_name = create_role_name,
            create_role_color = create_role_color,
            add_role = add_role,
            created_role = None
        )
        return await self.maps.get(service)(context)
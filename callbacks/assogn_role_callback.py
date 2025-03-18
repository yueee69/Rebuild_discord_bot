from profile_management.main_driver import Driver

import nextcord
from nextcord import Interaction

import random

class Main_handler:
    @staticmethod
    async def main(interaction: Interaction, user: nextcord.user, role: nextcord.role, service: str):
        return await Driver().get(
            interaction = interaction,
            service = service,
            target_user = user,
            add_role = role
        )
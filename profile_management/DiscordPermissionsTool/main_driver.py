from .feature.nick_name import Nick
from .feature.create_role import Create_role
from .feature.assign_role import Assign_role

class DiscordTools(Nick, Create_role, Assign_role):
    def __init__(self):
        pass
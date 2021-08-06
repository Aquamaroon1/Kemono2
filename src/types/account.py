from datetime import datetime
from typing import Optional, Union
from packaging.version import parse as parse_version

account_roles = ['consumer', 'moderator', 'administrator']

# class Agreement:
#     """
#     The user's agreement.
#     """
#     name: str
#     agreed_at: datetime
#     version: str
#     def is_outdated(self, version: str) -> bool:
#         current_version = parse_version(self.version)
#         new_version = parse_version(version)
#         return current_version < new_version

# class __Import:
#     """
#     The user's import.
#     """
#     id: str
#     service: str
#     approved: list[str]
#     rejected: list[str]
#     pending: list[str]

class Account:
    def __init__(self, 
        id: str,
        username: str,
        password: str,
        created_at: datetime,
        role: str = 'consumer'
    ) -> None:
        self.id = id
        self.username = username
        self.password = password
        self.created_at = created_at
        self.role = role if role else 'consumer'

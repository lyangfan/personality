"""
角色系统
"""
from .role_manager import RoleManager, get_role_manager
from ..models.personality import PersonalityProfile, RoleConfig, ResponseStyle, EmotionalTone

__all__ = [
    "RoleManager",
    "get_role_manager",
    "PersonalityProfile",
    "RoleConfig",
    "ResponseStyle",
    "EmotionalTone",
]

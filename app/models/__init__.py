# Każdy moduł z modelami musi być tu zaimportowany, inaczej Base.metadata nie zobaczy jego tabel.
from app.models.base import Base
from app.models.roles import Permission, Role, RolePermission, UserRole
from app.models.user import User, UserLoginData, UserProfile

__all__ = [
    "Base",
    "User",
    "UserProfile",
    "UserLoginData",
    "Role",
    "UserRole",
    "Permission",
    "RolePermission",
]

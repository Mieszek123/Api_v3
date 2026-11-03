import strawberry
import uuid

from datetime import datetime

from strawberry.permission import PermissionExtension

from app.gql.permissions import IsSelfOrSuperuser
from app.gql.types.profile import UserProfileType
from app.gql.types.roles import RoleType

# obcy user dostaje null zamiast błędu dla całego zapytania
def private_field():
    return strawberry.field(
        default=None,
        extensions=[PermissionExtension(permissions=[IsSelfOrSuperuser()], fail_silently=True)],
    )


@strawberry.type
class UserLoginDataType:
    last_login: datetime | None
    last_failed_login: datetime | None
    last_login_ip: str | None
    last_failed_login_ip: str | None
    failed_attempts: int
    locked_until: datetime | None


@strawberry.type
class UserType:
    id: uuid.UUID
    email: str | None = private_field()
    is_active: bool
    is_verified: bool
    created_at: datetime
    profile: UserProfileType | None
    login_data: UserLoginDataType | None = private_field()
    roles: list[RoleType]

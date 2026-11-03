import strawberry
import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from strawberry.types import Info

from app.db import async_session_maker
from app.gql.types import UserLoginDataType, UserType, profile_to_type, role_to_type
from app.models import Role as RoleModel, User as UserModel


async def get_user_type(user_id: uuid.UUID) -> UserType | None:
    async with async_session_maker() as session:
        user = await session.scalar(
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.login_data),
                selectinload(UserModel.roles).selectinload(RoleModel.permissions),
            )
        )

    if user is None:
        return None

    profile = profile_to_type(user.profile) if user.profile else None

    login_data = None
    if user.login_data:
        login_data = UserLoginDataType(
            last_login=user.login_data.last_login,
            last_failed_login=user.login_data.last_failed_login,
            last_login_ip=user.login_data.last_login_ip,
            last_failed_login_ip=user.login_data.last_failed_login_ip,
            failed_attempts=user.login_data.failed_attempts,
            locked_until=user.login_data.locked_until,
        )

    return UserType(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        profile=profile,
        login_data=login_data,
        roles=[role_to_type(role) for role in user.roles],
    )


@strawberry.type
class UserQuery:
    @strawberry.field
    async def me(self, info: Info) -> UserType | None:
        current_user = info.context["user"]
        if current_user is None:
            return None
        return await get_user_type(current_user.id)

    @strawberry.field
    async def user(self, info: Info, id: uuid.UUID) -> UserType | None:
        if info.context["user"] is None:
            raise PermissionError("Not authenticated")
        return await get_user_type(id)

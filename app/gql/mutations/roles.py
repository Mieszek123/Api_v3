import strawberry
import uuid

from sqlalchemy import delete
from strawberry.types import Info

from app.db import async_session_maker
from app.gql.permissions import require_superuser
from app.models import UserRole as UserRoleModel


@strawberry.type
class RolesMutation:
    @strawberry.mutation
    async def assign_role(self, info: Info, user_id: uuid.UUID, role_id: int) -> bool:
        require_superuser(info)

        async with async_session_maker() as session:
            session.add(UserRoleModel(user_id=user_id, role_id=role_id))
            await session.commit()
        return True

    @strawberry.mutation
    async def remove_role(self, info: Info, user_id: uuid.UUID, role_id: int) -> bool:
        require_superuser(info)

        async with async_session_maker() as session:
            result = await session.execute(
                delete(UserRoleModel).where(UserRoleModel.user_id == user_id, UserRoleModel.role_id == role_id)
            )
            await session.commit()
        return result.rowcount > 0

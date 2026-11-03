import strawberry

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from strawberry.types import Info

from app.db import async_session_maker
from app.gql.types import RoleType, role_to_type
from app.models import Role as RoleModel


@strawberry.type
class RolesQuery:
    @strawberry.field
    async def roles(self, info: Info) -> list[RoleType]:
        if info.context["user"] is None:
            raise PermissionError("Not authenticated")

        async with async_session_maker() as session:
            roles = await session.scalars(
                select(RoleModel).options(selectinload(RoleModel.permissions)).order_by(RoleModel.id)
            )

        return [role_to_type(role) for role in roles]

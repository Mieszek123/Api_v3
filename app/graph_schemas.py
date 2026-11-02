import strawberry
import uuid

from datetime import date, datetime
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from app.db import async_session_maker
from app.models import User as UserModel
from app.users import fastapi_users

optional_user = fastapi_users.current_user(active=True, optional=True)


@strawberry.type
class UserProfileType:
    username: str | None
    first_name: str | None
    last_name: str | None
    phone: str | None
    birth_date: date | None
    description: str | None
    profile_picture_url: str | None
    updated_at: datetime


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
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    profile: UserProfileType | None
    login_data: UserLoginDataType | None
    

@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info: Info) -> UserType | None:
        current_user = info.context["user"]
        if current_user is None:
            return None

        async with async_session_maker() as session:
            user = await session.scalar(
                select(UserModel)
                .where(UserModel.id == current_user.id)
                .options(selectinload(UserModel.profile), selectinload(UserModel.login_data))
            )

        profile = None
        if user.profile:
            profile = UserProfileType(
                username=user.profile.username,
                first_name=user.profile.first_name,
                last_name=user.profile.last_name,
                phone=user.profile.phone,
                birth_date=user.profile.birth_date,
                description=user.profile.description,
                profile_picture_url=user.profile.profile_picture_url,
                updated_at=user.profile.updated_at,
            )

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
        )



async def get_context(user: UserModel | None = Depends(optional_user)):
    return {"user": user}

schema = strawberry.Schema(query=Query)
graphql_router = GraphQLRouter(schema, context_getter=get_context)
import strawberry

from datetime import date, datetime

from app.models import UserProfile as UserProfileModel


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


@strawberry.input
class UserProfileInput:
    username: str | None = strawberry.UNSET
    first_name: str | None = strawberry.UNSET
    last_name: str | None = strawberry.UNSET
    phone: str | None = strawberry.UNSET
    birth_date: date | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    profile_picture_url: str | None = strawberry.UNSET


def profile_to_type(profile: UserProfileModel) -> UserProfileType:
    return UserProfileType(
        username=profile.username,
        first_name=profile.first_name,
        last_name=profile.last_name,
        phone=profile.phone,
        birth_date=profile.birth_date,
        description=profile.description,
        profile_picture_url=profile.profile_picture_url,
        updated_at=profile.updated_at,
    )

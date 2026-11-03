import strawberry

from strawberry.types import Info

from app.db import async_session_maker
from app.gql.types import UserProfileInput, UserProfileType, profile_to_type
from app.models import UserProfile as UserProfileModel


@strawberry.type
class ProfileMutation:
    @strawberry.mutation
    async def update_profile(self, info: Info, data: UserProfileInput) -> UserProfileType:
        current_user = info.context["user"]
        if current_user is None:
            raise PermissionError("Not authenticated")

        async with async_session_maker() as session:
            profile = await session.get(UserProfileModel, current_user.id)
            if profile is None:
                profile = UserProfileModel(user_id=current_user.id)
                session.add(profile)

            # UNSET = pole nie wysłane, None = wyczyść pole
            for field, value in vars(data).items():
                if value is not strawberry.UNSET:
                    setattr(profile, field, value)

            await session.commit()
            await session.refresh(profile)

        return profile_to_type(profile)

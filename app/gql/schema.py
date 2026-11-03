import strawberry

from fastapi import Depends
from strawberry.fastapi import GraphQLRouter

from app.gql.mutations import Mutation
from app.gql.queries import Query
from app.models import User as UserModel
from app.users import fastapi_users

optional_user = fastapi_users.current_user(active=True, optional=True)


async def get_context(user: UserModel | None = Depends(optional_user)):
    return {"user": user}


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_router = GraphQLRouter(schema, context_getter=get_context)

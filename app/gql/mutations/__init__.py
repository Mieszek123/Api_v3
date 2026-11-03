from strawberry.tools import merge_types

from app.gql.mutations.profile import ProfileMutation
from app.gql.mutations.roles import RolesMutation

Mutation = merge_types("Mutation", (ProfileMutation, RolesMutation))

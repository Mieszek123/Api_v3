from strawberry.tools import merge_types

from app.gql.queries.roles import RolesQuery
from app.gql.queries.user import UserQuery

Query = merge_types("Query", (UserQuery, RolesQuery))

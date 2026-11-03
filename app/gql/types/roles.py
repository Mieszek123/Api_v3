import strawberry

from app.models import Role as RoleModel


@strawberry.type
class PermissionType:
    id: int
    name: str
    description: str | None


@strawberry.type
class RoleType:
    id: int
    name: str
    description: str | None
    permissions: list[PermissionType]


def role_to_type(role: RoleModel) -> RoleType:
    return RoleType(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=[
            PermissionType(id=p.id, name=p.name, description=p.description)
            for p in role.permissions
        ],
    )

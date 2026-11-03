from typing import Any

from strawberry.permission import BasePermission
from strawberry.types import Info


def require_superuser(info: Info) -> None:
    current_user = info.context["user"]
    if current_user is None or not current_user.is_superuser:
        raise PermissionError("Forbidden")


class IsSelfOrSuperuser(BasePermission):
    """Pole widzi tylko właściciel konta albo superuser. source = obiekt UserType."""

    message = "Forbidden"

    def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        current_user = info.context["user"]
        if current_user is None:
            return False
        return current_user.is_superuser or current_user.id == source.id

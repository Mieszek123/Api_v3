import uuid
from datetime import date, datetime
from typing import Optional

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    profile: Mapped[Optional["UserProfile"]] = relationship(back_populates="user", passive_deletes=True)
    login_data: Mapped[Optional["UserLoginData"]] = relationship(back_populates="user", passive_deletes=True)
    roles: Mapped[list["Role"]] = relationship(secondary="user_roles", passive_deletes=True)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    username: Mapped[str | None] = mapped_column(String(50))
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    birth_date: Mapped[date | None]
    description: Mapped[str | None] = mapped_column(Text)
    profile_picture_url: Mapped[str | None] = mapped_column(String(500))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="profile")


class UserLoginData(Base):
    __tablename__ = "user_login_data"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_failed_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_ip: Mapped[str | None] = mapped_column(String(45))
    last_failed_login_ip: Mapped[str | None] = mapped_column(String(45))
    last_login_user_agent: Mapped[str | None] = mapped_column(Text)
    last_failed_login_user_agent: Mapped[str | None] = mapped_column(Text)
    failed_attempts: Mapped[int] = mapped_column(default=0, server_default="0")
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="login_data")

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    permissions: Mapped[list["Permission"]] = relationship(secondary="role_permissions", passive_deletes=True)

class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())



class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(Text)

class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User

# dzieci pytania: usuwane razem z nim (w bazie przez CASCADE, w ORM przez delete-orphan)
CHILDREN = dict(cascade="all, delete-orphan", passive_deletes=True)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(30))
    question_text: Mapped[str] = mapped_column(Text)
    max_score: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    # "metadata" jest zarezerwowane w SQLAlchemy, więc atrybut ma inną nazwę niż kolumna
    meta: Mapped[str | None] = mapped_column("metadata", Text)
    create_mode: Mapped[str | None] = mapped_column(String(30))
    is_archived: Mapped[bool] = mapped_column(default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    creator: Mapped["User"] = relationship()
    options: Mapped[list["QuestionOption"]] = relationship(
        back_populates="question", order_by="QuestionOption.position", **CHILDREN
    )
    media: Mapped[list["QuestionMedia"]] = relationship(
        back_populates="question", order_by="QuestionMedia.position", **CHILDREN
    )


class QuestionOption(Base):
    __tablename__ = "question_options"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    option_text: Mapped[str] = mapped_column(Text)
    position: Mapped[int]
    is_correct: Mapped[bool] = mapped_column(default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    question: Mapped["Question"] = relationship(back_populates="options")


class QuestionMedia(Base):
    __tablename__ = "question_media"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    media_url: Mapped[str] = mapped_column(Text)
    media_type: Mapped[str] = mapped_column(String(30))
    alt_text: Mapped[str | None] = mapped_column(Text)
    position: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    question: Mapped["Question"] = relationship(back_populates="media")

"""Podejścia do egzaminu: kto pisze (user albo anonim z kodu), jakie pytania wylosował i co odpowiedział."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.exams import Exam, ExamAccessCode
    from app.models.questions import Question, QuestionOption
    from app.models.user import User

CHILDREN = dict(cascade="all, delete-orphan", passive_deletes=True)


class AnonymousParticipant(Base):
    __tablename__ = "anonymous_participants"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    access_code_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_access_codes.id", ondelete="CASCADE"))
    display_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(320))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    access_code: Mapped["ExamAccessCode"] = relationship(back_populates="participants")
    instances: Mapped[list["ExamInstance"]] = relationship(back_populates="anonymous_participant", **CHILDREN)


class ExamInstance(Base):
    __tablename__ = "exam_instances"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"))
    # dokładnie jedno z dwóch: zalogowany user albo anonim z kodu dostępu
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    anonymous_participant_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("anonymous_participants.id", ondelete="CASCADE")
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    time_allowed_seconds: Mapped[int | None]
    status: Mapped[str] = mapped_column(String(20))
    score: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    max_score: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    attempt_number: Mapped[int] = mapped_column(default=1, server_default="1")
    random_seed: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    exam: Mapped["Exam"] = relationship(back_populates="instances")
    user: Mapped["User | None"] = relationship()
    anonymous_participant: Mapped["AnonymousParticipant | None"] = relationship(back_populates="instances")
    questions: Mapped[list["ExamInstanceQuestion"]] = relationship(
        back_populates="exam_instance", order_by="ExamInstanceQuestion.position", **CHILDREN
    )


class ExamInstanceQuestion(Base):
    """Pytanie, które trafiło do konkretnego podejścia (ze stałej listy albo wylosowane z puli)."""

    __tablename__ = "exam_instance_questions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    exam_instance_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_instances.id", ondelete="CASCADE"))
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    position: Mapped[int]
    is_mandatory: Mapped[bool] = mapped_column(default=False, server_default="false")
    origin: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    exam_instance: Mapped["ExamInstance"] = relationship(back_populates="questions")
    question: Mapped["Question"] = relationship()
    answers: Mapped[list["Answer"]] = relationship(back_populates="exam_instance_question", **CHILDREN)


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    exam_instance_question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exam_instance_questions.id", ondelete="CASCADE")
    )
    text_answer: Mapped[str | None] = mapped_column(Text)
    uploaded_file_url: Mapped[str | None] = mapped_column(Text)
    is_marked_correct: Mapped[bool | None]
    auto_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    manual_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    graded: Mapped[bool] = mapped_column(default=False, server_default="false")
    graded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # SET NULL: usunięcie oceniającego nie może kasować odpowiedzi studenta
    graded_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    exam_instance_question: Mapped["ExamInstanceQuestion"] = relationship(back_populates="answers")
    grader: Mapped["User | None"] = relationship()
    selected_options: Mapped[list["QuestionOption"]] = relationship(
        secondary="answer_selected_options", passive_deletes=True
    )


class AnswerSelectedOption(Base):
    __tablename__ = "answer_selected_options"

    answer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("answers.id", ondelete="CASCADE"), primary_key=True)
    option_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("question_options.id", ondelete="CASCADE"), primary_key=True
    )

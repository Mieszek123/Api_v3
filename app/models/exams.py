import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.courses import Course
    from app.models.groups import StudentGroup
    from app.models.instances import AnonymousParticipant, ExamInstance
    from app.models.printing import PrintingJob
    from app.models.questions import Question
    from app.models.user import User

# Dzieci egzaminu nie istnieją bez niego: usunięcie rodzica usuwa je w bazie (CASCADE),
# a cascade="all, delete-orphan" robi to samo po stronie ORM dla obiektów już załadowanych.
CHILDREN = dict(cascade="all, delete-orphan", passive_deletes=True)


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    # NULL = egzamin niepodpięty pod kurs
    course_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    exam_mode: Mapped[str] = mapped_column(String(20))
    # NULL = bez limitu czasu
    time_limit_seconds: Mapped[int | None]
    allow_page_leave: Mapped[bool] = mapped_column(default=False, server_default="false")
    allow_randomize: Mapped[bool] = mapped_column(default=False, server_default="false")
    allow_print: Mapped[bool] = mapped_column(default=False, server_default="false")
    is_published: Mapped[bool] = mapped_column(default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    creator: Mapped["User"] = relationship(back_populates="owned_exams")
    course: Mapped["Course | None"] = relationship(back_populates="exams")
    questions: Mapped[list["ExamQuestion"]] = relationship(
        back_populates="exam", order_by="ExamQuestion.position", **CHILDREN
    )
    group_assignments: Mapped[list["ExamGroup"]] = relationship(back_populates="exam", **CHILDREN)
    access_codes: Mapped[list["ExamAccessCode"]] = relationship(back_populates="exam", **CHILDREN)
    pools: Mapped[list["ExamPool"]] = relationship(back_populates="exam", **CHILDREN)
    instances: Mapped[list["ExamInstance"]] = relationship(back_populates="exam", **CHILDREN)
    printing_jobs: Mapped[list["PrintingJob"]] = relationship(back_populates="exam", **CHILDREN)


class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"))
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    position: Mapped[int]
    is_mandatory: Mapped[bool] = mapped_column(default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    exam: Mapped["Exam"] = relationship(back_populates="questions")
    question: Mapped["Question"] = relationship()


class ExamGroup(Base):
    """Przypisanie egzaminu do grupy studentów z oknem dostępności."""

    __tablename__ = "exam_groups"

    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), primary_key=True)
    group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("student_groups.id", ondelete="CASCADE"), primary_key=True
    )
    # NULL = bez ograniczenia z tej strony
    available_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    available_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    exam: Mapped["Exam"] = relationship(back_populates="group_assignments")
    group: Mapped["StudentGroup"] = relationship()


class ExamAccessCode(Base):
    __tablename__ = "exam_access_codes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"))
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    exam_code: Mapped[str] = mapped_column(String(32), unique=True)
    # NULL = bez limitu użyć / bez daty ważności
    max_uses: Mapped[int | None]
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    exam: Mapped["Exam"] = relationship(back_populates="access_codes")
    creator: Mapped["User"] = relationship()
    participants: Mapped[list["AnonymousParticipant"]] = relationship(back_populates="access_code", **CHILDREN)


class ExamPool(Base):
    __tablename__ = "exam_pools"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    context: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    exam: Mapped["Exam"] = relationship(back_populates="pools")
    groups: Mapped[list["ExamPoolGroup"]] = relationship(back_populates="pool", **CHILDREN)


class ExamPoolGroup(Base):
    __tablename__ = "exam_pool_groups"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pool_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_pools.id", ondelete="CASCADE"))
    group_name: Mapped[str] = mapped_column(String(100))
    # ile pytań wylosować z tej grupy
    pick_count: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    pool: Mapped["ExamPool"] = relationship(back_populates="groups")
    questions: Mapped[list["PoolQuestion"]] = relationship(back_populates="group", **CHILDREN)


class PoolQuestion(Base):
    __tablename__ = "pool_questions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_pool_groups.id", ondelete="CASCADE"))
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    is_mandatory: Mapped[bool] = mapped_column(default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    group: Mapped["ExamPoolGroup"] = relationship(back_populates="questions")
    question: Mapped["Question"] = relationship()

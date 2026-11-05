import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.exams import Exam
    from app.models.instances import ExamInstance
    from app.models.user import User


class PrintingJob(Base):
    __tablename__ = "printing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"))
    # NULL = wydruk całego egzaminu, nie konkretnego podejścia
    exam_instance_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("exam_instances.id", ondelete="CASCADE"))
    job_type: Mapped[str] = mapped_column(String(30))
    parameters: Mapped[str | None] = mapped_column(Text)
    result_url: Mapped[str | None] = mapped_column(Text)
    print_status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    creator: Mapped["User"] = relationship()
    exam: Mapped["Exam"] = relationship(back_populates="printing_jobs")
    exam_instance: Mapped["ExamInstance | None"] = relationship()

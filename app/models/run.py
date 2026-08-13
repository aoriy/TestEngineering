from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class TestRun(Base, TimestampMixin):
    __tablename__ = "test_run"

    id: Mapped[int] = mapped_column(primary_key=True)
    testcase_id: Mapped[int | None] = mapped_column(
        ForeignKey("testcase.id", ondelete="SET NULL")
    )
    environment_id: Mapped[int | None] = mapped_column(
        ForeignKey("environment.id", ondelete="SET NULL")
    )
    run_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    # pending / running / done / failed / timeout / cancelled

    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    exit_code: Mapped[int | None] = mapped_column(Integer)

    runs_dir: Mapped[str] = mapped_column(String(1024), default="")
    log_path: Mapped[str] = mapped_column(String(1024), default="")
    report_path: Mapped[str] = mapped_column(String(1024), default="")
    artifacts: Mapped[dict] = mapped_column(JSON, default=dict)


class SelfHealRecord(Base, TimestampMixin):
    __tablename__ = "self_heal_record"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(64), default="")
    shape_id: Mapped[int | None] = mapped_column(
        ForeignKey("shape.id", ondelete="SET NULL")
    )
    old_locator: Mapped[str] = mapped_column(Text, default="")
    new_locator: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(default=0.0)
    reasoning: Mapped[str] = mapped_column(Text, default="")
    page_snapshot: Mapped[str] = mapped_column(Text, default="")
    locator_version: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(32), default="suggest")
    # auto_applied / suggest / rejected

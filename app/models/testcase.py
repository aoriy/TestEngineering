from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.requirement import requirement_testcase


class TestCase(Base, TimestampMixin):
    __tablename__ = "testcase"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"), nullable=False
    )
    flow_id: Mapped[int | None] = mapped_column(
        ForeignKey("flow.id", ondelete="SET NULL")
    )
    environment_id: Mapped[int | None] = mapped_column(
        ForeignKey("environment.id", ondelete="SET NULL")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[str] = mapped_column(String(32), default="medium")
    status: Mapped[str] = mapped_column(String(32), default="draft")
    data_bindings: Mapped[dict] = mapped_column(JSON, default=dict)
    assertions: Mapped[list] = mapped_column(JSON, default=list)
    tags: Mapped[str] = mapped_column(String(512), default="")

    requirements: Mapped[list["Requirement"]] = relationship(
        secondary=requirement_testcase, back_populates="testcases"
    )
    data_rows: Mapped[list["TestData"]] = relationship(
        back_populates="testcase", cascade="all, delete-orphan"
    )


class TestData(Base, TimestampMixin):
    __tablename__ = "test_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    testcase_id: Mapped[int] = mapped_column(
        ForeignKey("testcase.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), default="")
    row: Mapped[dict] = mapped_column(JSON, default=dict)

    testcase: Mapped["TestCase"] = relationship(back_populates="data_rows")

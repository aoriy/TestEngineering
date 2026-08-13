from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Table, Text, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.testcase import TestCase


requirement_testcase = Table(
    "requirement_testcase",
    Base.metadata,
    Column(
        "requirement_id",
        ForeignKey("requirement.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "testcase_id",
        ForeignKey("testcase.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Requirement(Base, TimestampMixin):
    __tablename__ = "requirement"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"), nullable=False
    )
    module_id: Mapped[int | None] = mapped_column(
        ForeignKey("module.id", ondelete="SET NULL")
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(32), default="medium")
    status: Mapped[str] = mapped_column(String(32), default="draft")

    testcases: Mapped[list["TestCase"]] = relationship(
        secondary=requirement_testcase, back_populates="requirements"
    )

    @property
    def testcase_ids(self) -> list[int]:
        return [tc.id for tc in self.testcases]

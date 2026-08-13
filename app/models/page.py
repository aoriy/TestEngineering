from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class PageTemplate(Base, TimestampMixin):
    __tablename__ = "page_template"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"), nullable=False
    )
    module_id: Mapped[int | None] = mapped_column(
        ForeignKey("module.id", ondelete="SET NULL")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(512), default="")
    description: Mapped[str | None] = mapped_column(Text)

    shapes: Mapped[list["Shape"]] = relationship(
        back_populates="page_template", cascade="all, delete-orphan"
    )


class Shape(Base, TimestampMixin):
    __tablename__ = "shape"

    id: Mapped[int] = mapped_column(primary_key=True)
    page_template_id: Mapped[int] = mapped_column(
        ForeignKey("page_template.id", ondelete="CASCADE"), nullable=False
    )
    # input / button / select / checkbox / api / variable / code / assert / wait / condition
    shape_type: Mapped[str] = mapped_column(String(32), nullable=False)
    label: Mapped[str] = mapped_column(String(255), default="")

    # canvas layout
    x: Mapped[float] = mapped_column(default=0.0)
    y: Mapped[float] = mapped_column(default=0.0)
    width: Mapped[float] = mapped_column(default=120.0)
    height: Mapped[float] = mapped_column(default=40.0)
    style: Mapped[dict] = mapped_column(JSON, default=dict)

    # locator (versioned, ADR-0006 / ADR-0007)
    locator_type: Mapped[str] = mapped_column(
        String(32), default="data-testid"
    )  # data-testid / xpath / css / text
    locator_value: Mapped[str] = mapped_column(String(1024), default="")
    locator_history: Mapped[list] = mapped_column(JSON, default=list)
    locator_current: Mapped[int] = mapped_column(default=0)

    # api binding
    api_definition_id: Mapped[int | None] = mapped_column(
        ForeignKey("api_definition.id", ondelete="SET NULL")
    )
    api_params: Mapped[dict] = mapped_column(JSON, default=dict)
    extraction_rules: Mapped[dict] = mapped_column(JSON, default=dict)

    # value config
    value_source: Mapped[str] = mapped_column(String(32), default="literal")
    value: Mapped[str] = mapped_column(Text, default="")

    # code hooks (AST-guarded, ADR-0003)
    before_code: Mapped[str] = mapped_column(Text, default="")
    after_code: Mapped[str] = mapped_column(Text, default="")

    page_template: Mapped["PageTemplate"] = relationship(back_populates="shapes")


class ShapeType(Base, TimestampMixin):
    __tablename__ = "shape_type"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    default_style: Mapped[dict] = mapped_column(JSON, default=dict)

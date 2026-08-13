from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.page import PageTemplate


class Flow(Base, TimestampMixin):
    __tablename__ = "flow"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    nodes: Mapped[list["FlowNode"]] = relationship(
        back_populates="flow", cascade="all, delete-orphan"
    )
    edges: Mapped[list["FlowEdge"]] = relationship(
        back_populates="flow", cascade="all, delete-orphan"
    )


class FlowNode(Base, TimestampMixin):
    __tablename__ = "flow_node"

    id: Mapped[int] = mapped_column(primary_key=True)
    flow_id: Mapped[int] = mapped_column(
        ForeignKey("flow.id", ondelete="CASCADE"), nullable=False
    )
    page_template_id: Mapped[int] = mapped_column(
        ForeignKey("page_template.id", ondelete="CASCADE"), nullable=False
    )
    x: Mapped[float] = mapped_column(Float, default=0.0)
    y: Mapped[float] = mapped_column(Float, default=0.0)
    initial_vars: Mapped[dict] = mapped_column(JSON, default=dict)

    flow: Mapped["Flow"] = relationship(back_populates="nodes")
    page_template: Mapped["PageTemplate"] = relationship()
    steps: Mapped[list["Step"]] = relationship(
        back_populates="flow_node", cascade="all, delete-orphan"
    )

    @property
    def page_template_name(self) -> str:
        return self.page_template.name if self.page_template else ""


class Step(Base, TimestampMixin):
    __tablename__ = "step"

    id: Mapped[int] = mapped_column(primary_key=True)
    flow_node_id: Mapped[int] = mapped_column(
        ForeignKey("flow_node.id", ondelete="CASCADE"), nullable=False
    )
    shape_id: Mapped[int] = mapped_column(
        ForeignKey("shape.id", ondelete="CASCADE"), nullable=False
    )
    order: Mapped[int] = mapped_column(default=0, nullable=False)
    # click / input / select / assert / api_call / wait / condition / custom
    action_type: Mapped[str] = mapped_column(String(32), default="click")
    action_params: Mapped[dict] = mapped_column(JSON, default=dict)

    flow_node: Mapped["FlowNode"] = relationship(back_populates="steps")


class FlowEdge(Base, TimestampMixin):
    __tablename__ = "flow_edge"

    id: Mapped[int] = mapped_column(primary_key=True)
    flow_id: Mapped[int] = mapped_column(
        ForeignKey("flow.id", ondelete="CASCADE"), nullable=False
    )
    source_node_id: Mapped[int] = mapped_column(
        ForeignKey("flow_node.id", ondelete="CASCADE"), nullable=False
    )
    target_node_id: Mapped[int] = mapped_column(
        ForeignKey("flow_node.id", ondelete="CASCADE"), nullable=False
    )
    trigger: Mapped[str] = mapped_column(String(255), default="")

    flow: Mapped["Flow"] = relationship(back_populates="edges")

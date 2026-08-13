"""Self-heal orchestration (ADR-0005).

Triggered when a locator fails. Calls the LLM adapter, applies the three-layer
defense, versions the locator via Shape.locator_history, and writes an audit
record. `verify` (Playwright try-run) is injected by the UI executor.
"""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import SelfHealRecord, Shape
from app.services.selfheal import defense
from app.services.selfheal.llm import DeepSeekAdapter, HealSuggestion, LlmAdapter
from app.services.selfheal.prompts import truncate_html


def _latest_auto_applied(
    db: Session, shape_id: int, old_locator: str
) -> SelfHealRecord | None:
    return (
        db.query(SelfHealRecord)
        .filter(
            SelfHealRecord.shape_id == shape_id,
            SelfHealRecord.old_locator == old_locator,
            SelfHealRecord.status == "auto_applied",
        )
        .order_by(SelfHealRecord.id.desc())
        .first()
    )


def self_heal(
    db: Session,
    shape_id: int,
    old_locator: str,
    page_html: str = "",
    old_meta: dict | None = None,
    run_id: str = "",
    verify: defense.VerifyFn | None = None,
    adapter: LlmAdapter | None = None,
) -> dict:
    shape = db.get(Shape, shape_id)
    if shape is None:
        raise ValueError(f"shape {shape_id} not found")

    mode = settings.selfheal_mode
    if mode == "off":
        return {"status": "off", "shape_id": shape_id}

    cached = _latest_auto_applied(db, shape_id, old_locator)
    if cached is not None:
        return {
            "status": "cached",
            "new_locator": cached.new_locator,
            "locator_version": cached.locator_version,
            "confidence": cached.confidence,
        }

    llm = adapter or DeepSeekAdapter()
    suggestion: HealSuggestion = llm.suggest_locators(old_locator, page_html)

    applied = None
    reason = ""
    for candidate in suggestion.candidates:
        passed, why = defense.evaluate(
            candidate, suggestion.confidence, old_meta=old_meta, verify=verify
        )
        if passed:
            applied = candidate
            reason = why
            break
        reason = why

    record = SelfHealRecord(
        run_id=run_id,
        shape_id=shape.id,
        old_locator=old_locator,
        new_locator=applied.locator_value if applied else "",
        confidence=suggestion.confidence,
        reasoning=suggestion.reasoning,
        page_snapshot=truncate_html(page_html, 2000),
        locator_version=0,
        status="suggest",
    )
    db.add(record)

    if applied is not None and mode == "auto":
        version = _apply(db, shape, applied, record)
        record.status = "auto_applied"
        record.locator_version = version
        db.commit()
        return {
            "status": "auto_applied",
            "new_locator": applied.locator_value,
            "locator_type": applied.locator_type,
            "confidence": suggestion.confidence,
            "reasoning": suggestion.reasoning,
            "locator_version": version,
            "defense": reason,
        }

    db.commit()
    return {
        "status": "suggest",
        "candidates": [
            {
                "locator_type": c.locator_type,
                "locator_value": c.locator_value,
                "inner_text": c.inner_text,
                "role": c.role,
            }
            for c in suggestion.candidates
        ],
        "confidence": suggestion.confidence,
        "reasoning": suggestion.reasoning,
        "defense": reason,
    }


def _apply(db: Session, shape: Shape, candidate, record: SelfHealRecord) -> int:
    history = list(shape.locator_history or [])
    if not history:
        history.append(
            {
                "version": 0,
                "locator_type": shape.locator_type,
                "locator_value": shape.locator_value,
                "source": "manual",
            }
        )
    version = len(history)
    history.append(
        {
            "version": version,
            "locator_type": candidate.locator_type,
            "locator_value": candidate.locator_value,
            "source": "selfheal",
            "run_id": record.run_id,
        }
    )
    shape.locator_history = history
    shape.locator_current = version
    shape.locator_type = candidate.locator_type
    shape.locator_value = candidate.locator_value
    return version


def rollback(db: Session, shape_id: int) -> dict:
    shape = db.get(Shape, shape_id)
    if shape is None:
        raise ValueError(f"shape {shape_id} not found")
    history = list(shape.locator_history or [])
    if shape.locator_current <= 0 or not history:
        return {"status": "noop", "locator_current": shape.locator_current}

    prev = shape.locator_current - 1
    entry = history[prev]
    shape.locator_type = entry["locator_type"]
    shape.locator_value = entry["locator_value"]
    shape.locator_current = prev
    db.commit()
    return {
        "status": "rolled_back",
        "locator_current": prev,
        "locator_type": entry["locator_type"],
        "locator_value": entry["locator_value"],
    }

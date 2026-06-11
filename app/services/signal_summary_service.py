import json

from app.db.database import SessionLocal
from app.models.signal_summary import SignalSummary
from app.services.data_quality import compact_whitespace


def _summary_to_text(summary):
    if isinstance(summary, str):
        return compact_whitespace(summary)

    return json.dumps(summary or {}, ensure_ascii=True)


def save_signal_summary(
    company_id,
    signal_type,
    summary,
    narrative=None,
    key_changes=None,
    so_what=None,
):
    db = SessionLocal()

    try:
        summary_text = _summary_to_text(summary)
        summary_json = summary if isinstance(summary, dict) else None

        existing_summary = (
            db.query(SignalSummary)
            .filter(
                SignalSummary.company_id == company_id,
                SignalSummary.signal_type == signal_type,
            )
            .first()
        )

        if existing_summary:
            existing_summary.summary = summary_text
            existing_summary.category = signal_type
            existing_summary.summary_json = summary_json
            existing_summary.narrative = (
                compact_whitespace(narrative)
                or (
                    summary_json.get("narrative")
                    if summary_json
                    else summary_text
                )
            )
            existing_summary.key_changes = (
                key_changes
                if key_changes is not None
                else (
                    summary_json.get("key_changes")
                    if summary_json
                    else []
                )
            )
            existing_summary.so_what = (
                compact_whitespace(so_what)
                or (
                    summary_json.get("so_what")
                    if summary_json
                    else None
                )
            )
            db.commit()
            db.refresh(existing_summary)
            return existing_summary

        record = SignalSummary(
            company_id=company_id,
            signal_type=signal_type,
            category=signal_type,
            summary=summary_text,
            summary_json=summary_json,
            narrative=(
                compact_whitespace(narrative)
                or (
                    summary_json.get("narrative")
                    if summary_json
                    else summary_text
                )
            ),
            key_changes=(
                key_changes
                if key_changes is not None
                else (
                    summary_json.get("key_changes")
                    if summary_json
                    else []
                )
            ),
            so_what=(
                compact_whitespace(so_what)
                or (
                    summary_json.get("so_what")
                    if summary_json
                    else None
                )
            ),
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    finally:
        db.close()

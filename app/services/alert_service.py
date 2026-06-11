from app.db.database import SessionLocal
from app.models.alert import Alert
from app.services.data_quality import compact_whitespace


def save_alert(company_id, alert_type, message):
    db = SessionLocal()

    try:
        message = compact_whitespace(message)

        existing_alert = (
            db.query(Alert)
            .filter(
                Alert.company_id == company_id,
                Alert.message == message,
            )
            .first()
        )

        if existing_alert:
            return existing_alert

        alert = Alert(
            company_id=company_id,
            alert_type=alert_type,
            message=message,
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        return alert

    finally:
        db.close()

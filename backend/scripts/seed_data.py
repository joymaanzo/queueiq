"""Seed deterministic synthetic queue events and print a compact summary."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func

from app.database import SessionLocal
from app.models import Clinic, QueueEvent
from app.synthetic.generator import generate_synthetic_data


def main() -> None:
    inserted = generate_synthetic_data()
    db = SessionLocal()
    try:
        print("Events per clinic:")
        for clinic in db.query(Clinic).order_by(Clinic.clinic_id):
            count, avg_wait = db.query(
                func.count(QueueEvent.event_id), func.avg(QueueEvent.actual_wait_time_minutes)
            ).filter(QueueEvent.clinic_id == clinic.clinic_id).one()
            print(f"  {clinic.name}: {count} events, avg wait {avg_wait:.2f} minutes")

        central = db.query(Clinic).filter(Clinic.name == "Central Medical").one()
        print("Average wait by hour for Central Medical:")
        rows = db.query(
            QueueEvent.hour_of_day,
            func.avg(QueueEvent.actual_wait_time_minutes),
        ).filter(QueueEvent.clinic_id == central.clinic_id).group_by(
            QueueEvent.hour_of_day
        ).order_by(QueueEvent.hour_of_day).all()
        for hour, avg_wait in rows:
            print(f"  {hour:02d}:00: {avg_wait:.2f} minutes")
        print(f"Inserted this run: {sum(inserted.values())} events")
    finally:
        db.close()


if __name__ == "__main__":
    main()
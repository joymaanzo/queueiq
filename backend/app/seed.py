from app.database import SessionLocal
from app.models import Clinic, QueueEvent


def seed_if_empty(session):
    """Idempotently seed clinics and queue events when the database is empty."""
    if session.query(Clinic).count() == 0:
        session.add_all([
            Clinic(
                name="Central Medical",
                location="Downtown",
                service_type="GP",
                capacity_doctors=4,
                capacity_patients_per_day=80,
                hours_open="07:00-19:00",
                days_open="Mon-Fri",
            ),
            Clinic(
                name="Midtown Urgent Care",
                location="Midtown",
                service_type="Urgent Care",
                capacity_doctors=2,
                capacity_patients_per_day=40,
                hours_open="09:00-17:00",
                days_open="Mon-Sat",
            ),
            Clinic(
                name="Riverside Family Dental",
                location="Riverside",
                service_type="Dental",
                capacity_doctors=2,
                capacity_patients_per_day=20,
                hours_open="08:00-16:00",
                days_open="Tue-Fri",
            ),
        ])
        session.commit()
        print("[seed] Inserted 3 clinics.")

    if session.query(QueueEvent).count() == 0:
        from app.synthetic.generator import generate_all

        generate_all(session)
        print("[seed] Generated queue events.")

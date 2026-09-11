"""
SQLAlchemy models for QueueIQ.
Mirrors Section 12 of product-spec.md.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Clinic(Base):
    __tablename__ = "clinics"

    clinic_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    service_type = Column(String, nullable=False)
    capacity_doctors = Column(Integer, nullable=False)
    capacity_patients_per_day = Column(Integer, nullable=False)
    hours_open = Column(String, nullable=False)
    days_open = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    queue_events = relationship("QueueEvent", back_populates="clinic")
    predictions = relationship("Prediction", back_populates="clinic")
    model_parameters = relationship("ModelParameter", back_populates="clinic")
    hourly_stats = relationship("ClinicHourlyStat", back_populates="clinic")


class QueueEvent(Base):
    __tablename__ = "queue_events"

    event_id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.clinic_id"), nullable=False)
    patient_id = Column(String, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    service_start_time = Column(DateTime, nullable=False)
    service_end_time = Column(DateTime, nullable=False)
    actual_wait_time_minutes = Column(Float, nullable=False)
    service_duration_minutes = Column(Float, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    hour_of_day = Column(Integer, nullable=False)

    clinic = relationship("Clinic", back_populates="queue_events")


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.clinic_id"), nullable=False)
    timestamp_of_prediction = Column(DateTime, default=datetime.utcnow)
    predicted_wait_time_minutes = Column(Float, nullable=False)
    confidence_interval_lower = Column(Float, nullable=False)
    confidence_interval_upper = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=False, default=0.80)
    actual_wait_time_minutes = Column(Float, nullable=True)
    reported_at = Column(DateTime, nullable=True)

    clinic = relationship("Clinic", back_populates="predictions")


class ModelParameter(Base):
    __tablename__ = "model_parameters"

    param_id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.clinic_id"), nullable=False)
    param_name = Column(String, nullable=False)
    param_value = Column(Float, nullable=False)
    fitted_at = Column(DateTime, default=datetime.utcnow)
    data_points_used = Column(Integer, nullable=False, default=0)

    clinic = relationship("Clinic", back_populates="model_parameters")


class ClinicHourlyStat(Base):
    __tablename__ = "clinic_hourly_stats"

    stat_id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.clinic_id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    hour_of_day = Column(Integer, nullable=False)
    avg_wait_minutes = Column(Float, nullable=False)
    std_wait_minutes = Column(Float, nullable=False)
    sample_count = Column(Integer, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)

    clinic = relationship("Clinic", back_populates="hourly_stats")

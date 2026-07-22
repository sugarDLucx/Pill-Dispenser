from sqlalchemy import Column, Integer, String, Date
from backend.database import Base

class MedicationSchedule(Base):
    __tablename__ = "medication_schedules"

    compartment_id = Column(Integer, primary_key=True, index=True) # 1 to 10
    medicine_name = Column(String, index=True)
    frequency = Column(String) # e.g., "Daily", "Weekly"
    time_slots = Column(String) # e.g., "08:00,20:00"
    start_date = Column(Date)
    end_date = Column(Date)

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_mobile = Column(String, default="")
    caretakers = Column(String, default="") # Comma-separated list of phone numbers

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import threading

from backend.database import engine, Base, get_db
from backend.models import MedicationSchedule, SystemSettings
from backend.hardware_daemon import mark_medicine_taken, main_loop, current_temperature

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Pill Dispenser API")

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start hardware daemon in background
@app.on_event("startup")
def startup_event():
    daemon_thread = threading.Thread(target=main_loop, daemon=True)
    daemon_thread.start()

# --- Pydantic Models ---
class ScheduleCreate(BaseModel):
    compartment_id: int
    medicine_name: str
    frequency: str
    time_slots: str
    start_date: date
    end_date: date

class ScheduleResponse(ScheduleCreate):
    class Config:
        orm_mode = True

class SettingsUpdate(BaseModel):
    caretaker_primary_mobile: str
    caretaker_secondary_mobile: Optional[str] = ""

# --- Endpoints ---
@app.get("/api/schedule", response_model=List[ScheduleResponse])
def get_schedules(db: Session = Depends(get_db)):
    return db.query(MedicationSchedule).all()

@app.post("/api/schedule", response_model=ScheduleResponse)
def create_or_update_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    db_schedule = db.query(MedicationSchedule).filter(MedicationSchedule.compartment_id == schedule.compartment_id).first()
    if db_schedule:
        for key, value in schedule.dict().items():
            setattr(db_schedule, key, value)
    else:
        db_schedule = MedicationSchedule(**schedule.dict())
        db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@app.post("/api/settings")
def update_settings(settings: SettingsUpdate, db: Session = Depends(get_db)):
    db_settings = db.query(SystemSettings).first()
    if db_settings:
        db_settings.caretaker_primary_mobile = settings.caretaker_primary_mobile
        db_settings.caretaker_secondary_mobile = settings.caretaker_secondary_mobile
    else:
        db_settings = SystemSettings(**settings.dict())
        db.add(db_settings)
    db.commit()
    return {"status": "success"}

@app.get("/api/status")
def get_status(db: Session = Depends(get_db)):
    # Calculate next dose
    schedules = db.query(MedicationSchedule).all()
    next_dose_time = "None"
    next_dose_med = "None"
    from datetime import datetime
    now = datetime.now()
    current_time_str = now.strftime("%H:%M")
    
    closest_time = None
    closest_med = None
    earliest_time = None
    earliest_med = None
    
    for schedule in schedules:
        if not schedule.time_slots: continue
        slots = schedule.time_slots.split(",")
        for slot in slots:
            slot = slot.strip()
            
            # Track the absolute earliest slot in the day (for tomorrow's wraparound)
            if earliest_time is None or slot < earliest_time:
                earliest_time = slot
                earliest_med = schedule.medicine_name

            # Track the closest future slot (for today)
            if slot > current_time_str:
                if closest_time is None or slot < closest_time:
                    closest_time = slot
                    closest_med = schedule.medicine_name
                    
    # If a future time exists today, use it. Otherwise, use tomorrow's earliest time.
    next_time_val = closest_time if closest_time else earliest_time
    next_med_val = closest_med if closest_time else earliest_med
                    
    if next_time_val:
        h, m = next_time_val.split(":")
        hour = int(h)
        ampm = "PM" if hour >= 12 else "AM"
        hour = hour % 12
        hour = hour if hour else 12
        next_dose_time = f"{hour:02d}:{m} {ampm}"
        if not closest_time and next_time_val:
            next_dose_time += " (Tomorrow)"
        next_dose_med = next_med_val

    return {
        "temperature": current_temperature,
        "next_dose_time": next_dose_time,
        "next_dose_med": next_dose_med,
        "network_status": "Connected",
        "gsm_status": "Active"
    }

@app.post("/api/medicine-taken")
def medicine_taken():
    mark_medicine_taken()
    return {"status": "Alarm Cancelled"}

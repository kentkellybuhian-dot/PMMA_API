from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# =========================
# DATABASE CONNECTION
# =========================

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# =========================
# MODELS
# =========================

class LeaveRecord(BaseModel):
    name: str
    leave_type: str
    start_date: str
    end_date: str
    destination: str
    days: float
    entry_id: str
    type: str
    region: str
    unit_assignment: str
    processed_by: str


class RosterRecord(BaseModel):
    name: str
    date_assigned: str
    date_relieved: Optional[str] = None
    unit_assigned: str
    previous_unit: str
    authority: str
    remarks: str

# =========================
# ROOT CHECK
# =========================

@app.get("/")
def home():
    return {"message": "PMMA API with DB is LIVE"}

@app.get("/test-db")
def test_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT 1")
    result = cur.fetchone()

    cur.close()
    conn.close()

    return {"db_status": "connected", "result": result}

# =========================
# LEAVE DATA
# =========================

@app.get("/leave")
def get_leave():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM leave_data ORDER BY id")
    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


@app.post("/leave")
def upload_leave(record: LeaveRecord):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO leave_data (
            name, leave_type, start_date, end_date,
            destination, days, entry_id, type,
            region, unit_assignment, processed_by
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (entry_id)
        DO UPDATE SET
            name = EXCLUDED.name,
            leave_type = EXCLUDED.leave_type,
            start_date = EXCLUDED.start_date,
            end_date = EXCLUDED.end_date,
            destination = EXCLUDED.destination,
            days = EXCLUDED.days,
            type = EXCLUDED.type,
            region = EXCLUDED.region,
            unit_assignment = EXCLUDED.unit_assignment,
            processed_by = EXCLUDED.processed_by
    """, (
        record.name, record.leave_type, record.start_date,
        record.end_date, record.destination, record.days,
        record.entry_id, record.type, record.region,
        record.unit_assignment, record.processed_by
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "success"}

# =========================
# ROSTER DATA
# =========================

@app.get("/roster")
def get_roster():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM roster_data")
    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


@app.post("/roster")
def upload_roster(record: RosterRecord):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO roster_data (
            name, date_assigned, date_relieved,
            unit_assigned, previous_unit,
            authority, remarks
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (name, date_assigned)
        DO UPDATE SET
            date_relieved = EXCLUDED.date_relieved,
            unit_assigned = EXCLUDED.unit_assigned,
            previous_unit = EXCLUDED.previous_unit,
            authority = EXCLUDED.authority,
            remarks = EXCLUDED.remarks
    """, (
        record.name,
        record.date_assigned,
        None if record.date_relieved == "" else record.date_relieved,
        record.unit_assigned,
        record.previous_unit,
        record.authority,
        record.remarks
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "success"}

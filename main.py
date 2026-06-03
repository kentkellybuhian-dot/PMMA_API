from fastapi import FastAPI
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
# TEST API
# =========================
@app.get("/")
def home():
    return {"message": "PMMA API is LIVE with Database"}

# =========================
# GET LEAVE DATA
# =========================
@app.get("/leave")
def get_leave():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM leave_data")
    data = cur.fetchall()

    cur.close()
    conn.close()

    return data

# =========================
# GET ROSTER DATA
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

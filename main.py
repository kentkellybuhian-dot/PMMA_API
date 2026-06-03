from fastapi import FastAPI
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

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

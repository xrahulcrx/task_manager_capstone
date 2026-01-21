from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import sqlite3

app = FastAPI(title="Task Manager API (SQLite)")

DB_FILE = "tasks.db"


# ---------- DB HELPERS ----------
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # makes rows behave like dict
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        status TEXT NOT NULL CHECK(status IN ('pending', 'done'))
    )
    """)

    conn.commit()
    conn.close()


@app.on_event("startup")
def startup_event():
    init_db()


# ---------- MODELS ----------
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default="", max_length=300)
    status: str = Field(default="pending")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    status: Optional[str] = None


# ---------- ROUTES ----------
@app.get("/tasks")
def list_tasks():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


@app.post("/tasks")
def create_task(task: TaskCreate):
    if task.status not in ["pending", "done"]:
        raise HTTPException(status_code=400, detail="status must be pending or done")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)",
        (task.title, task.description, task.status)
    )
    conn.commit()

    task_id = cursor.lastrowid
    conn.close()

    return {
        "message": "Task created",
        "task": {
            "id": task_id,
            "title": task.title,
            "description": task.description,
            "status": task.status
        }
    }


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    existing = dict(row)

    new_title = task.title if task.title is not None else existing["title"]
    new_description = task.description if task.description is not None else existing["description"]
    new_status = task.status if task.status is not None else existing["status"]

    if new_status not in ["pending", "done"]:
        conn.close()
        raise HTTPException(status_code=400, detail="status must be pending or done")

    cursor.execute("""
        UPDATE tasks
        SET title = ?, description = ?, status = ?
        WHERE id = ?
    """, (new_title, new_description, new_status, task_id))

    conn.commit()
    conn.close()

    return {
        "message": "Task updated",
        "task": {
            "id": task_id,
            "title": new_title,
            "description": new_description,
            "status": new_status
        }
    }


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return {"message": "Task deleted"}

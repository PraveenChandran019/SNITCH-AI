import sqlite3
from datetime import datetime

DB = "tasks.db"


def conn():
    return sqlite3.connect(DB, check_same_thread=False)


# ---------------- INIT ----------------
def init_db():
    c = conn()
    cur = c.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        task TEXT,
        deadline TEXT,
        status TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        last_active TIMESTAMP
    )
    """)

    c.commit()
    c.close()


# ---------------- USERS ----------------
def add_user(uid, name):
    c = conn()
    cur = c.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO users (id, name, last_active) VALUES (?, ?, ?)",
        (uid, name, datetime.now())
    )

    c.commit()
    c.close()


def update_user_activity(uid):
    c = conn()
    cur = c.cursor()

    cur.execute(
        "UPDATE users SET last_active=? WHERE id=?",
        (datetime.now(), uid)
    )

    c.commit()
    c.close()


def get_user_name_from_db(uid):
    c = conn()
    cur = c.cursor()

    cur.execute("SELECT name FROM users WHERE id=?", (uid,))
    row = cur.fetchone()

    c.close()

    return row[0] if row else uid


# ---------------- TASKS ----------------
def add_task(user, task, deadline):
    c = conn()
    cur = c.cursor()

    cur.execute(
        "INSERT INTO tasks (user, task, deadline, status) VALUES (?, ?, ?, ?)",
        (user, task, deadline, "pending")
    )

    c.commit()
    c.close()


def complete_task(user):
    c = conn()
    cur = c.cursor()

    cur.execute(
        "UPDATE tasks SET status='done' WHERE user=? AND status='pending'",
        (user,)
    )

    c.commit()
    c.close()


def task_exists(user, task):
    c = conn()
    cur = c.cursor()

    cur.execute(
        "SELECT 1 FROM tasks WHERE user=? AND task LIKE ? AND status='pending'",
        (user, f"%{task}%")
    )

    exists = cur.fetchone()

    c.close()
    return exists is not None


def get_tasks():
    c = conn()
    cur = c.cursor()

    cur.execute("SELECT user, task, deadline, status FROM tasks")
    data = cur.fetchall()

    c.close()
    return data
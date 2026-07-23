"""
SQLite storage for user accounts and saved analyses.

We use Python's built-in sqlite3 module — no external database server, just a
single file (tarra.db) sitting in the project root. Each function opens its own
short-lived connection, runs one query, and closes it. That's slightly less
efficient than a shared connection pool, but it's the simplest thing that's
correct, and Tarra's traffic is tiny.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone

# The database file lives at the project root, next to pyproject.toml.
# __file__ is src/db.py, so two dirnames up gets us to the project root.
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tarra.db')


def _now():
    """Current UTC time as an ISO-8601 string, e.g. '2026-06-16T14:03:00+00:00'."""
    return datetime.now(timezone.utc).isoformat()


def get_connection():
    """
    Open a connection to the database.

    row_factory = sqlite3.Row makes query results behave like dictionaries
    (row['username']) instead of plain tuples (row[1]) — much easier to read.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create the tables if they don't already exist.

    Safe to call every time the app starts — 'IF NOT EXISTS' means it won't
    wipe or duplicate anything on subsequent runs.
    """
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS analyses (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            filename     TEXT    NOT NULL,
            summary_json TEXT    NOT NULL,
            notes_json   TEXT    NOT NULL,
            created_at   TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)
    conn.commit()
    conn.close()


# ── Users ──────────────────────────────────────────────────────────────────────

def create_user(username, password_hash):
    """
    Insert a new user and return their new id.

    Raises sqlite3.IntegrityError if the username is already taken (the UNIQUE
    constraint on the column enforces this) — callers should check availability
    first for a friendly message, but this is the real safety net.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, password_hash, _now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_user_by_username(username):
    """Return the user row matching this username, or None if there isn't one."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Return the user row with this id, or None."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()


# ── Analyses ───────────────────────────────────────────────────────────────────

def save_analysis(user_id, filename, summary, notes):
    """
    Save one completed analysis for a user and return its new id.

    `summary` (a dict) and `notes` (a list) are serialised to JSON strings so
    they fit in a single text column each. We pull them back out with
    json.loads() when displaying.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO analyses (user_id, filename, summary_json, notes_json, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, filename, json.dumps(summary), json.dumps(notes), _now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def list_analyses(user_id):
    """
    Return a user's saved analyses, newest first, for the history page.

    Deliberately skips notes_json — the history list only needs the summary,
    and the notes blob can be large. The full notes load on the detail view.
    """
    conn = get_connection()
    try:
        return conn.execute(
            """SELECT id, filename, summary_json, created_at
               FROM analyses WHERE user_id = ? ORDER BY created_at DESC""",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()


def get_analysis(analysis_id, user_id):
    """
    Return one saved analysis by id — but only if it belongs to this user.

    Scoping the query to user_id is what stops someone from viewing another
    person's analysis by guessing the id in the URL (/analysis/5).
    """
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM analyses WHERE id = ? AND user_id = ?",
            (analysis_id, user_id),
        ).fetchone()
    finally:
        conn.close()

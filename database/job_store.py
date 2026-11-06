import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"


def initialize_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            url TEXT,
            date_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            score INTEGER,
            match_level TEXT,
            notified INTEGER DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()


def job_exists(job_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT job_id FROM jobs WHERE job_id = ?",
        (str(job_id),)
    )

    result = cursor.fetchone()
    connection.close()

    return result is not None


def save_job(job):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO jobs
        (job_id, title, company, location, url, score, match_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        str(job["id"]),
        job["title"],
        job.get("company", "MongoDB"),
        job["location"],
        job["url"],
        job["score"],
        job["match_level"]
    ))

    connection.commit()
    inserted = cursor.rowcount > 0
    connection.close()

    return inserted

def get_unnotified_jobs():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT job_id, title, company, location, url, score, match_level
        FROM jobs
        WHERE notified = 0
    """)

    jobs = [dict(row) for row in cursor.fetchall()]

    connection.close()
    return jobs


def mark_job_notified(job_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE jobs
        SET notified = 1
        WHERE job_id = ?
    """, (str(job_id),))

    connection.commit()
    connection.close()

def mark_all_existing_as_notified():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE jobs
        SET notified = 1
    """)

    connection.commit()
    connection.close()

    print("Existing vacancies marked as processed.")
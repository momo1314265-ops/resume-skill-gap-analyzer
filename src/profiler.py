# src/profiler.py
import logging
import sqlite3
from pathlib import Path


def profile_database(input_dir: Path):
    """
    Day4: Data Profiling
    Profiles the jobs.db database
    """
    print("📊 Profiling Database:...")

    db_path = input_dir / "jobs.db"
    if not db_path.exists():
        print("⚠️ No database found at", db_path)
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total records
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total = cursor.fetchone()[0]

    # Records with missing fields
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE job_title IS NULL OR company IS NULL OR description IS NULL")
    missing_fields = cursor.fetchone()[0]

    # Average description length
    cursor.execute("SELECT AVG(LENGTH(description)) FROM jobs")
    avg_desc_len = cursor.fetchone()[0]

    conn.close()

    print("\n📊 Profile Summary:")
    print(f"Total Records: {total}")
    print(f"Records with Missing Fields: {missing_fields}")
    print(f"Average Description Length: {int(avg_desc_len) if avg_desc_len else 0} characters")


if __name__ == "__main__":
    GOLD_DIR = Path(__file__).parent.parent / "3_gold"
    profile_database(GOLD_DIR)

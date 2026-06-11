# src/loader.py
import json
import logging
import sqlite3
from pathlib import Path


def load_all_jsons(input_dir: Path, output_dir: Path):
    """
    Day 3: Gold Layer Loader
    Loads processed JSON files from silver layer to SQLite database (jobs.db)
    """
    print("🥇 Gold:...")

    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = output_dir / "jobs.db"

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            source_id TEXT PRIMARY KEY,
            job_title TEXT,
            company TEXT,
            description TEXT,
            tech_stack TEXT
        )
    """)
    conn.commit()

    json_files = list(input_dir.glob("*.json")) if input_dir.exists() else []
    total = len(json_files)
    inserted = 0
    skipped = 0

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Tech stack is empty for now (will be populated in week 2/3)
            tech_stack = ""

            # Insert or ignore (idempotent)
            cursor.execute("""
                INSERT OR IGNORE INTO jobs
                (source_id, job_title, company, description, tech_stack)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data["source_id"],
                data["job_title"],
                data["company"],
                data["description"],
                tech_stack
            ))
            conn.commit()

            if cursor.rowcount > 0:
                logging.info(f"✅ Inserted: {json_file.name}")
                inserted += 1
            else:
                logging.info(f"⏭️ Skipped (duplicate): {json_file.name}")
                skipped += 1
        except Exception as e:
            logging.warning(f"⚠️ Failed to load: {json_file.name}, Error: {e}")
            skipped += 1

    conn.close()

    print("\n📊 Gold Summary:")
    print(f"Total: {total} | Inserted: {inserted} | Skipped: {skipped}")


if __name__ == "__main__":
    SILVER_DIR = Path(__file__).parent.parent / "2_silver"
    GOLD_DIR = Path(__file__).parent.parent / "3_gold"
    load_all_jsons(SILVER_DIR, GOLD_DIR)

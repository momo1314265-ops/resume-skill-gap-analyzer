import logging
import sys
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html
from src.loader import load_all_jsons
from src.profiler import profile_database

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

SOURCE_DIR = Path("0_source")
BRONZE_DIR = Path("1_bronze")
SILVER_DIR = Path("2_silver")
GOLD_DIR = Path("3_gold")


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python main.py "
            "[ingest|process|load|profile]"
        )
        return

    command = sys.argv[1]

    match command:
        case "ingest":
            ingest_all_mhtml(
                SOURCE_DIR,
                BRONZE_DIR
            )

        case "process":
            process_all_html(
                BRONZE_DIR,
                SILVER_DIR
            )

        case "load":
            load_all_jsons(
                SILVER_DIR,
                GOLD_DIR
            )

        case "profile":
            profile_database(
                GOLD_DIR
            )

        case _:
            print("Unknown command")


if __name__ == "__main__":
    main()
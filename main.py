# main.py
import sys
from src.ingestor import extract_mhtml_to_html

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        print("🚀 Starting Day 1: Bronze Layer Extraction...\n")
        extract_mhtml_to_html()
    else:
        print("Usage:")
        print("  python main.py ingest   - Run MHTML → HTML extractor (Bronze Layer)")

if __name__ == "__main__":
    main()
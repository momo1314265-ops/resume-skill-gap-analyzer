# src/ingestor.py
import logging
import quopri
from email import policy
from email.parser import BytesParser
from pathlib import Path


def ingest_all_mhtml(input_dir: Path, output_dir: Path):
    """
    Day 1: Bronze Layer Extractor
    Reads .mhtml from input_dir, decodes it, saves clean .html to output_dir
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    mhtml_files = list(input_dir.glob("*.mhtml")) if input_dir.exists() else []
    total = len(mhtml_files)
    extracted = 0
    failed = 0

    # Required header
    print("🥉 Bronze:...")

    for file_path in mhtml_files:
        try:
            with open(file_path, "rb") as f:
                msg = BytesParser(policy=policy.default).parse(f)

            html_payload = None
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_payload = part.get_payload(decode=False)
                    break

            if not html_payload:
                logging.warning(f"⚠️ No HTML content found in: {file_path.name}")
                failed += 1
                continue

            try:
                decoded_html = quopri.decodestring(html_payload).decode("utf-8", errors="ignore")
            except Exception:
                decoded_html = html_payload

            output_name = file_path.stem + ".html"
            output_path = output_dir / output_name

            with open(output_path, "w", encoding="utf-8") as out_file:
                out_file.write(decoded_html)

            logging.info(f"✅ Extracted: {file_path.name}")
            extracted += 1

        except Exception:
            logging.error(f"❌ Failed: {file_path.name}")
            failed += 1

    # Required summary output
    print("\n📊 Bronze Summary:")
    print(f"Total: {total} | Extracted: {extracted} | Failed: {failed}")


if __name__ == "__main__":
    SOURCE_DIR = Path(__file__).parent.parent / "0_source"
    BRONZE_DIR = Path(__file__).parent.parent / "1_bronze"
    ingest_all_mhtml(SOURCE_DIR, BRONZE_DIR)
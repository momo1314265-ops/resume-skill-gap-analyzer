# src/ingestor.py
import quopri
from email import policy
from email.parser import BytesParser
from pathlib import Path

# Fixed path definitions
SOURCE_DIR = Path(__file__).parent.parent / "0_source"
BRONZE_DIR = Path(__file__).parent.parent / "1_bronze"

# Function name MUST BE extract_mhtml_to_html (matches main.py import)
def extract_mhtml_to_html() -> None:
    """
    Day 1: Bronze Layer Extractor
    Reads .mhtml from 0_source/, decodes it, saves clean .html to 1_bronze/
    """
    # Create bronze folder if missing
    BRONZE_DIR.mkdir(exist_ok=True)

    # Get all mhtml files
    mhtml_files = list(SOURCE_DIR.glob("*.mhtml"))
    print(f"📥 Found {len(mhtml_files)} MHTML files to process")

    for file_path in mhtml_files:
        try:
            # Read mhtml binary
            with open(file_path, "rb") as f:
                msg = BytesParser(policy=policy.default).parse(f)

            html_payload = None
            # Locate text/html part
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_payload = part.get_payload(decode=False)
                    break

            if not html_payload:
                print(f"⚠️ No HTML content in {file_path.name}")
                continue

            # Decode quoted-printable encoding
            try:
                decoded_html = quopri.decodestring(html_payload).decode("utf-8", errors="ignore")
            except Exception:
                decoded_html = html_payload

            # Save html to bronze folder
            output_name = file_path.stem + ".html"
            output_path = BRONZE_DIR / output_name

            with open(output_path, "w", encoding="utf-8") as out_file:
                out_file.write(decoded_html)

            print(f"✅ Extracted: {file_path.name} → {output_name}")

        except Exception as err:
            print(f"❌ Failed {file_path.name}: {str(err)}")

    print("\n🎉 Bronze Layer complete! All files saved to 1_bronze/")

# Test run when executing ingestor.py directly
if __name__ == "__main__":
    extract_mhtml_to_html()
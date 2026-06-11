# src/processor.py
import json
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError

# Fixed absolute project paths
BRONZE_DIR = Path(__file__).parent.parent / "1_bronze"
SILVER_DIR = Path(__file__).parent.parent / "2_silver"

# Pydantic Data Contract (all string fields as required)
class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str

def clean_html_text(raw_text: str) -> str:
    """Normalize whitespace, prevent fused words from stripped HTML tags"""
    if not raw_text:
        return ""
    # Collapse multiple spaces/newlines/tabs to single space
    return " ".join(raw_text.split())

# Mandatory required function name & parameters
def process_all_html(input_dir: Path, output_dir: Path):
    logging.info("🥈 Silver: Starting HTML file processing pipeline")

    # Create output folder recursively if missing (idempotent requirement)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Guard clause if bronze input folder does not exist
    if not input_dir.exists():
        logging.warning("⚠️ Bronze source directory not found.")
        print("\n📊 Silver Summary:")
        print("Total: 0 | Processed: 0 | Skipped: 0")
        return

    html_files = list(input_dir.glob("*.html"))
    total = len(html_files)
    processed = 0
    skipped = 0

    for html_file in html_files:
        try:
            # Safe UTF-8 read with error fallback
            html_content = html_file.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(html_content, "html.parser")

            # 1. Extract source_id from og:url meta tag
            og_url_meta = soup.find("meta", property="og:url")
            if not og_url_meta or not og_url_meta.get("content"):
                logging.warning(f"Missing og:url source_id metadata in: {html_file.name}")
                skipped += 1
                continue

            raw_url = og_url_meta["content"].strip()
            source_id = raw_url.rstrip("/").split("/")[-1]
            if not source_id.strip():
                logging.warning(f"Extracted empty source_id from URL for: {html_file.name}")
                skipped += 1
                continue

            # 2. Extract Job Title (Jobstreet official data-automation tag)
            title_tag = soup.find(attrs={"data-automation": "job-detail-title"})
            if not title_tag:
                logging.warning(f"Missing job_title element in: {html_file.name}")
                skipped += 1
                continue
            raw_title = title_tag.get_text(separator=" ", strip=True)
            job_title = clean_html_text(raw_title)

            # 3. Extract Company Name
            company_tag = soup.find(attrs={"data-automation": "advertiser-name"})
            if not company_tag:
                logging.warning(f"Missing company element in: {html_file.name}")
                skipped += 1
                continue
            raw_company = company_tag.get_text(separator=" ", strip=True)
            company = clean_html_text(raw_company)

            # 4. Extract Full Job Description
            desc_tag = soup.find(attrs={"data-automation": "jobAdDetails"})
            if not desc_tag:
                logging.warning(f"Missing description block in: {html_file.name}")
                skipped += 1
                continue
            raw_desc = desc_tag.get_text(separator=" ", strip=True)
            description = clean_html_text(raw_desc)

            # 5. Validate data shape with Pydantic model
            validated_job = JobListing(
                source_id=source_id,
                job_title=job_title,
                company=company,
                description=description
            )

            # Save JSON named by source_id (overwrites old file, no duplicate copies)
            output_json_path = output_dir / f"{source_id}.json"
            with open(output_json_path, "w", encoding="utf-8") as out_file:
                json.dump(validated_job.model_dump(), out_file, ensure_ascii=False, indent=2)

            logging.info(f"✅ Processed: {html_file.name}")
            processed += 1

        except ValidationError as val_err:
            logging.warning(f"❌ Pydantic validation failed for {html_file.name}: {str(val_err)}")
            skipped += 1
        except Exception as general_err:
            logging.error(f"❌ Critical failure processing {html_file.name} | Error: {str(general_err)}")
            skipped += 1

    # Final human-readable summary print (explicitly allowed per task instructions)
    print("\n📊 Silver Summary:")
    print(f"Total: {total} | Processed: {processed} | Skipped: {skipped}")

# Self-test execution when running this file directly
if __name__ == "__main__":
    process_all_html(input_dir=BRONZE_DIR, output_dir=SILVER_DIR)
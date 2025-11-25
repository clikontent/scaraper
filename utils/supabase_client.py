import os
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing Supabase environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def insert_job(job: dict):
    """
    Inserts a job row into external_jobs table.
    Checks for duplicates by external_id first.
    Logs scraping results into 'scraping_logs'.
    """
    payload = {
        "external_id": job.get("external_id") or None,
        "title": job.get("title") or None,
        "company": job.get("company") or None,
        "description": job.get("description") or None,
        "location": job.get("location") or None,
        "job_type": job.get("job_type") or None,
        "salary": job.get("salary") or None,
        "experience_level": job.get("experience_level") or None,
        "skills": job.get("skills") or [],
        "requirements": job.get("requirements") or [],
        "posted_date": job.get("posted_date") or None,
        "application_url": job.get("application_url") or None,
        "company_logo": job.get("company_logo") or None,
        "source": job.get("source") or None,
        "category": job.get("category") or None,
        "raw_data": job.get("raw_data") or {},
        "created_at": None,
        "updated_at": None,
    }

    result = {"ok": True, "duplicate": False, "error": None}

    try:
        # Check for duplicate
        existing = supabase.table("external_jobs") \
            .select("id") \
            .eq("external_id", payload["external_id"]) \
            .execute()

        if existing.data and len(existing.data) > 0:
            result["duplicate"] = True
        else:
            supabase.table("external_jobs").insert(payload).execute()

        # Log scraping
        supabase.table("scraping_logs").insert({
            "source": payload["source"],
            "external_id": payload["external_id"],
            "status": "duplicate" if result["duplicate"] else "inserted",
            "scraped_at": datetime.utcnow().isoformat()
        }).execute()

    except Exception as e:
        result["ok"] = False
        result["error"] = str(e)
        print("❌ Error inserting job:", e)

    return result

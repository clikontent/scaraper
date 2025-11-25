# cron.py

import asyncio
from datetime import datetime
from utils.supabase_client import supabase
from scrapers.job_websites import SCRAPERS


def insert_job(job):
    """
    Insert a single job into Supabase, avoiding duplicates by external_id or url.
    Fill missing columns with None.
    """
    query = (
        supabase.table("external_jobs")
        .select("id")
        .or_(f"external_id.eq.{job.get('external_id')},url.eq.{job.get('url')}")
        .execute()
    )

    if query.data:
        print(f"Skipping duplicate job: {job.get('title')} at {job.get('company')}")
        return

    job_record = {
        "external_id": job.get("external_id"),
        "title": job.get("title"),
        "company": job.get("company"),
        "description": job.get("description"),
        "location": job.get("location"),
        "job_type": job.get("job_type"),
        "salary": job.get("salary"),
        "experience_level": job.get("experience_level"),
        "skills": job.get("skills") or [],
        "requirements": job.get("requirements") or [],
        "posted_date": job.get("posted_date"),
        "application_url": job.get("application_url"),
        "company_logo": job.get("company_logo"),
        "source": job.get("source"),
        "category": job.get("category"),
        "raw_data": job.get("raw_data") or {},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    supabase.table("external_jobs").insert(job_record).execute()
    print(f"Inserted job: {job.get('title')} at {job.get('company')}")


async def run_scrapers():
    for scraper in SCRAPERS:
        print(f"Running scraper: {scraper.__name__}")

        try:
            # Await async scrapers
            jobs = await scraper()

            if not jobs:
                print("No jobs returned.")
                continue

            for job in jobs:
                insert_job(job)

        except Exception as e:
            print(f"Error running scraper {scraper.__name__}: {e}")


def main():
    asyncio.run(run_scrapers())


if __name__ == "__main__":
    main()

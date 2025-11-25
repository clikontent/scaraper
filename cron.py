# cron.py

import asyncio
import inspect
from datetime import datetime
from utils.supabase_client import supabase
from scrapers.job_websites import SCRAPERS


async def run_scraper_function(scraper):
    """Safely run sync or async scraper."""
    if inspect.iscoroutinefunction(scraper):
        return await scraper()
    else:
        from asyncio import to_thread
        return await to_thread(scraper)


def insert_job(job):
    external_id = job.get("external_id") or ""
    url = job.get("url") or ""

    try:
        query = (
            supabase.table("external_jobs")
            .select("id")
            .or_(f"external_id.eq.{external_id},url.eq.{url}")
            .execute()
        )
    except Exception as e:
        print("Duplicate check error:", e)
        return

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

    try:
        supabase.table("external_jobs").insert(job_record).execute()
        print(f"Inserted job: {job.get('title')} at {job.get('company')}")
    except Exception as e:
        print("Insert error:", e)


async def run_scrapers():
    for scraper in SCRAPERS:
        print(f"\nRunning scraper: {scraper.__name__}")

        try:
            jobs = await run_scraper_function(scraper)

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

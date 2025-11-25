import asyncio
from scrapers.job_websites import SCRAPERS
from supabase_client import insert_job


async def run_all_scrapers():
    print("🚀 Running scheduled African remote job scraper...\n")

    total = 0

    for scraper in SCRAPERS:
        try:
            print(f"🔎 Running {scraper.__name__}...")

            jobs = await scraper()
            print(f" → {len(jobs)} scraped")

            for job in jobs:
                insert_job(job)

            total += len(jobs)
            print(f" ✓ Inserted {len(jobs)} jobs\n")

        except Exception as e:
            print(f"❌ Error in {scraper.__name__}: {e}")

    print(f"🏁 Done! Total jobs scraped: {total}")


if __name__ == "__main__":
    asyncio.run(run_all_scrapers())

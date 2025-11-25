import asyncio
from scrapers.remoteok import scrape_remoteok
from scrapers.indeed import scrape_indeed
from supabase_client import insert_job

# Add more scrapers if needed
SCRAPERS = [
   scrape_remoteok,
    scrape_remote_africa,
    scrape_weworkremotely
]


async def run_scrapers():
    print("🚀 Starting African remote job scrape...\n")

    for scraper in SCRAPERS:
        try:
            print(f"🔎 Running {scraper.__name__}...")

            jobs = await scraper()

            print(f" → {len(jobs)} jobs scraped")

            for job in jobs:
                insert_job(job)

            print(f" ✓ Inserted {len(jobs)} jobs into Supabase\n")

        except Exception as e:
            print(f"❌ Error running scraper {scraper.__name__}: {e}\n")


if __name__ == "__main__":
    asyncio.run(run_scrapers())

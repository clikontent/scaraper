import asyncio
import inspect
from scrapers.remoteok import scrape_remoteok
from scrapers.remote_africa import scrape_remote_africa
from scrapers.weworkremotely import scrape_weworkremotely
from scrapers.climatechangecareers import scrape_climatechangecareers
from scrapers.nodesk import scrape_nodesk
from scrapers.remoterocketship import scrape_remoterocketship

from supabase_client import insert_job


SCRAPERS = [
    scrape_remoteok,
    scrape_remote_africa,
    scrape_weworkremotely,
    scrape_climatechangecareers,
    scrape_nodesk,
    scrape_remoterocketship
]


async def run_scraper_function(scraper):
    """Runs scraper whether it is async or normal."""
    if inspect.iscoroutinefunction(scraper):
        return await scraper()
    else:
        from asyncio import to_thread
        return await to_thread(scraper)


async def run_scrapers():
    print("🚀 Starting African remote job scrape...\n")

    for scraper in SCRAPERS:
        try:
            print(f"🔎 Running {scraper.__name__}...")

            jobs = await run_scraper_function(scraper)

            if not jobs:
                print(" → 0 jobs returned\n")
                continue

            print(f" → {len(jobs)} jobs scraped")

            for job in jobs:
                insert_job(job)

            print(f" ✓ Inserted {len(jobs)} jobs into Supabase\n")

        except Exception as e:
            print(f"❌ Error running scraper {scraper.__name__}: {e}\n")


if __name__ == "__main__":
    asyncio.run(run_scrapers())

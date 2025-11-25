import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone

URL = "https://weworkremotely.com/top-trending-remote-jobs"

async def scrape_weworkremotely():
    jobs = []

    async with aiohttp.ClientSession() as session:
        async with session.get(URL, headers={"User-Agent": "Mozilla/5.0"}) as res:
            html = await res.text()

    soup = BeautifulSoup(html, "html.parser")
    listings = soup.select("li.feature")

    now = datetime.now(timezone.utc)  # UTC datetime for timestamps

    for li in listings:
        try:
            title_el = li.select_one("span.title")
            company_el = li.select_one("span.company")
            url_el = li.find("a")

            title = title_el.text.strip() if title_el else None
            company = company_el.text.strip() if company_el else None
            url = "https://weworkremotely.com" + url_el.get("href")

            job = {
                "external_id": url,  # unique ID for duplicates
                "title": title,
                "company": company,
                "description": None,
                "location": "Remote (Global)",
                "job_type": None,
                "salary": None,
                "experience_level": None,
                "skills": [],
                "requirements": [],
                "posted_date": now,  # datetime object for timestamptz
                "application_url": url,
                "company_logo": None,
                "source": "WeWorkRemotely",
                "category": None,
                "raw_data": {
                    "html": str(li),
                    "scraped_at": now.isoformat(),  # JSON-safe
                },
            }

            jobs.append(job)

        except Exception as e:
            print("WeWorkRemotely error:", e)

    return jobs

import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone

URL = "https://remoteafrica.io"

async def scrape_remote_africa():
    jobs = []

    async with aiohttp.ClientSession() as session:
        async with session.get(URL, headers={"User-Agent": "Mozilla/5.0"}) as res:
            html = await res.text()

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.job-card")

    now = datetime.now(timezone.utc)  # UTC datetime for timestamps

    for card in cards:
        try:
            title = card.select_one("h2").text.strip()
            company_el = card.select_one(".company")
            company = company_el.text.strip() if company_el else None
            url_el = card.select_one("a")
            url = "https://remoteafrica.io" + url_el.get("href") if url_el else None

            job = {
                "external_id": url,
                "title": title,
                "company": company,
                "description": None,
                "location": "Remote (Africa)",
                "job_type": None,
                "salary": None,
                "experience_level": None,
                "skills": [],
                "requirements": [],
                "posted_date": now,  # datetime object for timestamptz
                "application_url": url,
                "company_logo": None,
                "source": "RemoteAfrica",
                "category": None,
                "raw_data": {
                    "html": str(card),
                    "scraped_at": now.isoformat(),  # JSON-safe string
                },
            }

            jobs.append(job)

        except Exception as e:
            print("RemoteAfrica error:", e)

    return jobs

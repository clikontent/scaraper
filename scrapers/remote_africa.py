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

    # UPDATED SELECTOR
    cards = soup.select("a.job-card__link")

    now = datetime.now(timezone.utc)

    for card in cards:
        try:
            title_el = card.select_one(".job-card__title")
            company_el = card.select_one(".job-card__company")

            title = title_el.get_text(strip=True) if title_el else None
            company = company_el.get_text(strip=True) if company_el else None

            url = "https://remoteafrica.io" + card.get("href")

            jobs.append({
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
                "posted_date": now,
                "application_url": url,
                "company_logo": None,
                "source": "RemoteAfrica",
                "category": None,
                "raw_data": {
                    "html": str(card),
                    "scraped_at": now.isoformat(),
                },
            })

        except Exception as e:
            print("RemoteAfrica error:", e)

    return jobs

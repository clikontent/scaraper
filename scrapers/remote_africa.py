import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://remoteafrica.io"


async def scrape_remote_africa():
    jobs = []

    async with aiohttp.ClientSession() as session:
        async with session.get(URL, headers={"User-Agent": "Mozilla/5.0"}) as res:
            html = await res.text()

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.job-card")

    for card in cards:
        try:
            title = card.select_one("h2").text.strip()
            company = card.select_one(".company").text.strip() if card.select_one(".company") else None
            location = "Remote (Africa)"
            url = "https://remoteafrica.io" + card.select_one("a").get("href")

            job = {
                "external_id": url,
                "title": title,
                "company": company,
                "description": None,
                "location": location,
                "job_type": None,
                "salary": None,
                "experience_level": None,
                "skills": [],
                "requirements": [],
                "posted_date": datetime.utcnow().isoformat(),
                "application_url": url,
                "company_logo": None,
                "source": "RemoteAfrica",
                "category": None,
                "raw_data": {
                    "html": str(card),
                    "scraped_at": datetime.utcnow().isoformat(),
                },
            }

            jobs.append(job)

        except Exception as e:
            print("RemoteAfrica error:", e)

    return jobs


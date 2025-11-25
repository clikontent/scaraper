import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://beyondthesavannah.co.ke"

async def scrape_beyondthesavannah():
    jobs = []

    async with aiohttp.ClientSession() as session:
        async with session.get(URL, headers={"User-Agent": "Mozilla/5.0"}) as res:
            html = await res.text()

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.job-card")

    for card in cards:
        try:
            title_el = card.select_one("h3.job-title")
            company_el = card.select_one(".company-name")
            url_el = card.select_one("a.apply-button")

            title = title_el.text.strip() if title_el else None
            company = company_el.text.strip() if company_el else None
            url = url_el.get("href") if url_el else None

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
                "posted_date": datetime.utcnow().isoformat(),
                "application_url": url,
                "company_logo": None,
                "source": "BeyondTheSavannah",
                "category": None,
                "raw_data": {
                    "html": str(card),
                    "scraped_at": datetime.utcnow().isoformat()
                },
            }

            jobs.append(job)

        except Exception as e:
            print("BeyondTheSavannah error:", e)

    return jobs
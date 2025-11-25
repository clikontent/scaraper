import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.brightermonday.co.ke/jobs/remote"

async def scrape_brightermonday():
    jobs = []

    async with aiohttp.ClientSession() as session:
        async with session.get(URL, headers={"User-Agent": "Mozilla/5.0"}) as res:
            html = await res.text()

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("div.job-item")

    for row in rows:
        try:
            title_el = row.select_one("h2.job-title a")
            company_el = row.select_one(".job-company")
            url = title_el.get("href") if title_el else None

            title = title_el.text.strip() if title_el else None
            company = company_el.text.strip() if company_el else None

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
                "source": "BrighterMonday",
                "category": None,
                "raw_data": {
                    "html": str(row),
                    "scraped_at": datetime.utcnow().isoformat()
                },
            }

            jobs.append(job)

        except Exception as e:
            print("BrighterMonday error:", e)

    return jobs

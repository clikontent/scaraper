import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://remoteok.com/?location=Worldwide&search=remote"


async def scrape_remoteok():
    jobs = []

    async with aiohttp.ClientSession() as session:
        async with session.get(URL, headers={"User-Agent": "Mozilla/5.0"}) as res:
            html = await res.text()

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tr.job")

    for row in rows:
        try:
            title = row.get("data-search") or None
            company = row.get("data-company") or None
            url = "https://remoteok.com" + (row.get("data-url") or "")
            skills = [tag.text.strip() for tag in row.select(".tag")]

            job = {
                "external_id": row.get("data-id") or url,
                "title": title,
                "company": company,
                "description": None,
                "location": row.get("data-location"),
                "job_type": None,
                "salary": None,
                "experience_level": None,
                "skills": skills,
                "requirements": [],
                "posted_date": datetime.utcnow().isoformat(),
                "application_url": url,
                "company_logo": None,
                "source": "RemoteOK",
                "category": None,
                "raw_data": {
                    "html": str(row),
                    "scraped_at": datetime.utcnow().isoformat(),
                },
            }

            jobs.append(job)

        except Exception as e:
            print("RemoteOK error:", e)

    return jobs

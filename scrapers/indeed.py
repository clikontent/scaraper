import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

INDEED_URL = "https://www.indeed.com/jobs?q=remote&l=Africa"


async def scrape_indeed():
    jobs = []

    async with aiohttp.ClientSession() as session:
        async with session.get(INDEED_URL, headers={"User-Agent": "Mozilla/5.0"}) as response:
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.job_seen_beacon")

    for card in cards:
        try:
            title_el = card.select_one("h2.jobTitle span")
            company_el = card.select_one(".companyName")
            location_el = card.select_one(".companyLocation")
            url_el = card.find("a", {"class": "jcs-JobTitle"})

            title = title_el.text.strip() if title_el else None
            company = company_el.text.strip() if company_el else None
            location = location_el.text.strip() if location_el else None

            url = None
            if url_el and url_el.get("href"):
                url = "https://www.indeed.com" + url_el.get("href")

            job = {
                "external_id": url,  # using URL as unique ID
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
                "source": "Indeed",
                "category": None,
                "raw_data": {
                    "html": str(card),
                    "scraped_at": datetime.utcnow().isoformat(),
                },
            }

            jobs.append(job)

        except Exception as e:
            print("Indeed parse error:", e)

    return jobs

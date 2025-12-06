import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin

BASE_URL = "https://www.climatechangecareers.com"
REMOTE_JOBS_URL = BASE_URL + "/jobs/?remote=remote"

async def scrape_climatechangecareers(max_pages=5):
    jobs = []

    async with aiohttp.ClientSession() as session:
        for page in range(1, max_pages + 1):
            url = REMOTE_JOBS_URL + f"&page={page}"
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as res:
                html = await res.text()

            soup = BeautifulSoup(html, "html.parser")
            job_cards = soup.select("div.job-card, li.job-card, article.job-card")

            if not job_cards:
                print(f"No jobs found on page {page}")
                break

            for card in job_cards:
                try:
                    title_el = card.select_one("h2 a, h3 a")
                    company_el = card.select_one(".company, .job-company")
                    location_el = card.select_one(".location, .job-location")
                    link_el = card.select_one("a")

                    title = title_el.get_text(strip=True) if title_el else None
                    company = company_el.get_text(strip=True) if company_el else None
                    location = location_el.get_text(strip=True) if location_el else "Remote"
                    link = urljoin(BASE_URL, link_el["href"]) if link_el else None

                    posted_date = datetime.now(timezone.utc)  # No posted date visible on list page

                    if title and company and link:
                        jobs.append({
                            "external_id": link,
                            "title": title,
                            "company": company,
                            "description": None,  # Can fetch detail page if needed
                            "location": location,
                            "job_type": None,
                            "salary": None,
                            "experience_level": None,
                            "skills": [],
                            "requirements": [],
                            "posted_date": posted_date,
                            "application_url": link,
                            "company_logo": None,
                            "source": "ClimateChangeCareers",
                            "category": None,
                            "raw_data": str(card)
                        })
                except Exception as e:
                    print("Climate jobs error:", e)

    return jobs

# Example test
# import asyncio
# jobs = asyncio.run(scrape_climatechangecareers())
# print(f"Found {len(jobs)} jobs")

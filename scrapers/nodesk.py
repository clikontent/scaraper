import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin

BASE_URL = "https://nodesk.co/remote-jobs/"

async def scrape_nodesk(max_pages=5):
    jobs = []

    async with aiohttp.ClientSession() as session:
        for page in range(1, max_pages + 1):
            url = BASE_URL
            if page > 1:
                url = f"{BASE_URL}?page={page}"

            try:
                async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                    resp.raise_for_status()
                    html = await resp.text()
            except Exception as e:
                print(f"NoDesk error on page {page}: {e}")
                break

            soup = BeautifulSoup(html, "html.parser")
            job_cards = soup.select("div.job-card, article.job-card, li.job-card")

            if not job_cards:
                print(f"No jobs found on page {page}")
                break

            for card in job_cards:
                try:
                    title_el = card.select_one("h2 a, h3 a")
                    company_el = card.select_one(".company, .company-name")
                    location_el = card.select_one(".location, .job-location")
                    link_el = card.select_one("a")

                    title = title_el.get_text(strip=True) if title_el else None
                    company = company_el.get_text(strip=True) if company_el else None
                    location = location_el.get_text(strip=True) if location_el else "Remote"
                    link = urljoin(BASE_URL, link_el["href"]) if link_el else None
                    posted_date = datetime.now(timezone.utc)

                    if title and company and link:
                        jobs.append({
                            "external_id": link,
                            "title": title,
                            "company": company,
                            "description": None,  # Could fetch job page for full description
                            "location": location,
                            "job_type": None,
                            "salary": None,
                            "experience_level": None,
                            "skills": [],
                            "requirements": [],
                            "posted_date": posted_date,
                            "application_url": link,
                            "company_logo": None,
                            "source": "NoDesk",
                            "category": None,
                            "raw_data": str(card),
                        })
                except Exception as e:
                    print("NoDesk job parse error:", e)

    return jobs

# Example usage:
# import asyncio
# jobs = asyncio.run(scrape_nodesk(max_pages=2))
# print(f"Found {len(jobs)} jobs")

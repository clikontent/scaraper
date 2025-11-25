import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import asyncio

BASE_URL = "https://www.climatechangecareers.com"
REMOTE_JOBS_URL = BASE_URL + "/jobs/remote/"

def clean_html(html):
    """Convert HTML to clean plain text."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n")
    return text.strip()

async def fetch_page(session, url):
    async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as res:
        return await res.text()

async def scrape_climatechangecareers():
    jobs = []
    page_number = 1
    has_next_page = True

    async with aiohttp.ClientSession() as session:
        while has_next_page:
            url = REMOTE_JOBS_URL + f"?page={page_number}"
            page_text = await fetch_page(session, url)
            soup = BeautifulSoup(page_text, "html.parser")

            # Adjust selector to match actual job cards
            job_cards = soup.select("div.job-listing, li.job-listing")
            if not job_cards:
                break  # No more jobs found

            for card in job_cards:
                try:
                    title_el = card.select_one("h2.job-title a, .job-title a")
                    title = title_el.get_text(strip=True) if title_el else None

                    link = title_el["href"] if title_el and title_el.has_attr("href") else None
                    if link and link.startswith("/"):
                        link = BASE_URL + link

                    company_el = card.select_one(".job-company, .company")
                    company = company_el.get_text(strip=True) if company_el else None

                    location_el = card.select_one(".job-location, .location")
                    location = location_el.get_text(strip=True) if location_el else "Remote"

                    date_el = card.select_one(".date-posted, .posted-date")
                    posted_date = None
                    if date_el:
                        date_text = date_el.get_text(strip=True)
                        try:
                            posted_date = datetime.strptime(date_text, "%d %b %Y").replace(tzinfo=timezone.utc)
                        except Exception:
                            posted_date = datetime.now(timezone.utc)

                    description = ""
                    if link:
                        job_page = await fetch_page(session, link)
                        job_soup = BeautifulSoup(job_page, "html.parser")
                        desc_el = job_soup.select_one(".job-description, .description")
                        description_html = desc_el.decode_contents() if desc_el else ""
                        description = clean_html(description_html)

                    job = {
                        "external_id": link,
                        "title": title,
                        "company": company,
                        "description": description,
                        "location": location,
                        "job_type": None,
                        "salary": None,
                        "experience_level": None,
                        "skills": [],
                        "requirements": [],
                        "posted_date": posted_date or datetime.now(timezone.utc),
                        "application_url": link,
                        "company_logo": None,
                        "source": "ClimateChangeCareers",
                        "category": None,
                        "raw_data": {
                            "html": str(card),
                            "scraped_at": datetime.now(timezone.utc).isoformat(),
                        },
                    }
                    jobs.append(job)
                except Exception as e:
                    print("Error scraping climatechangecareers job card:", e)

            # Check if a "Next" page exists
            next_page_el = soup.select_one("a.next, .pagination-next")
            if next_page_el and "disabled" not in next_page_el.get("class", []):
                page_number += 1
            else:
                has_next_page = False

    return jobs

# Example usage
# asyncio.run(scrape_climatechangecareers())

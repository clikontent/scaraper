import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin

BASE_URL = "https://nodesk.co/remote-jobs/"

def scrape_nodesk(max_pages=5):
    """
    Scrapes jobs from NoDesk remote-jobs list.
    Returns a list of job dicts.
    """
    jobs = []

    for page in range(1, max_pages + 1):
        url = BASE_URL
        if page > 1:
            url = f"{BASE_URL}?page={page}"
        try:
            resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Inspect the site to find correct selector for job entries
            # Note: NoDesk uses JS / dynamic loading — might need to handle that
            job_cards = soup.select("div.job-card, li.job, .remote-job-item")  # example selectors

            if not job_cards:
                # if no job cards found, stop paging
                break

            for card in job_cards:
                title_el = card.select_one("h2, h3, .job-title")
                company_el = card.select_one(".company, .company-name")
                link_el = card.select_one("a")
                location_el = card.select_one(".location, .job-location")

                title = title_el.get_text(strip=True) if title_el else None
                company = company_el.get_text(strip=True) if company_el else None
                raw_link = link_el["href"] if link_el and link_el.get("href") else None
                link = urljoin(BASE_URL, raw_link) if raw_link else None
                location = location_el.get_text(strip=True) if location_el else None

                posted_at = datetime.now(timezone.utc).isoformat()

                if title and company and link:
                    jobs.append({
                        "external_id": link,
                        "title": title,
                        "company": company,
                        "description": None,
                        "location": location,
                        "job_type": None,
                        "salary": None,
                        "experience_level": None,
                        "skills": [],
                        "requirements": [],
                        "posted_date": posted_at,
                        "application_url": link,
                        "company_logo": None,
                        "source": "NoDesk",
                        "category": None,
                        "raw_data": {
                            "html": str(card),
                            "scraped_at": posted_at
                        }
                    })
        except Exception as e:
            print("NoDesk scraper error on page", page, ":", e)
            continue

    return jobs

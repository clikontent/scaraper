import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin
import asyncio # Only needed if you plan to run the script directly for testing

# Note: requests is intentionally not imported as aiohttp is used

BASE_URL = "https://nodesk.co/remote-jobs/"

async def scrape_nodesk(max_pages=5):
    """
    Scrapes jobs from NoDesk remote-jobs list using aiohttp.
    Returns a list of job dicts.
    """
    jobs = []

    # Use ClientSession for connection pooling and better performance
    async with aiohttp.ClientSession() as session:
        for page in range(1, max_pages + 1):
            url = BASE_URL
            if page > 1:
                url = f"{BASE_URL}?page={page}"
            
            print(f"Scraping NoDesk page {page} at {url}...") # Optional debug print

            try:
                # Asynchronous request with user agent header
                async with session.get(
                    url, 
                    timeout=aiohttp.ClientTimeout(total=15), 
                    headers={"User-Agent": "Mozilla/5.0"}
                ) as resp:
                    resp.raise_for_status()
                    
                    # Await the response text
                    text = await resp.text() 
                    soup = BeautifulSoup(text, "html.parser")

                    # Inspect the site to find correct selector for job entries
                    # Note: NoDesk uses JS / dynamic loading — might need to handle that
                    # Using common selectors as placeholders
                    job_cards = soup.select("div.job-card, li.job, .remote-job-item") 

                    if not job_cards:
                        # If no job cards found, stop paging
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

# Example of how to run this function for testing purposes
# if __name__ == '__main__':
#     results = asyncio.run(scrape_nodesk(max_pages=1))
#     print(f"Found {len(results)} jobs.")
#     # for job in results:
#     #     print(job['title'])

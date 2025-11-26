import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

BASE_URL = "https://www.remoterocketship.com/?page=1&sort=DateAdded&locations=Africa?ref=oscarw5"

def remoterocketship(max_pages=15):
    """
    Scrape RemoteRocketship jobs filtered by Africa.
    Automatically paginates until jobs stop.
    """
    jobs = []

    for page in range(1, max_pages + 1):
        url = BASE_URL.format(page=page)

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.select("div.job-listing-item")

            # Stop when no more jobs
            if not job_cards:
                break

            for card in job_cards:
                title_el = card.select_one(".job-title")
                company_el = card.select_one(".company-name")
                link_el = card.select_one("a")
                location_el = card.select_one(".job-location")

                title = title_el.get_text(strip=True) if title_el else None
                company = company_el.get_text(strip=True) if company_el else None
                link = (
                    "https://www.remoterocketship.com" + link_el["href"]
                    if link_el and link_el.get("href")
                    else None
                )
                location = (
                    location_el.get_text(strip=True) if location_el else "Remote"
                )

                # Only allow Africa jobs (your URL already filters Africa)
                # But this protects against future changes
                if "africa" not in location.lower():
                    continue

                posted_at = datetime.now(timezone.utc).isoformat()

                if title and company and link:
                    jobs.append({
                        "title": title,
                        "company": company,
                        "url": link,
                        "location": location,
                        "source": "RemoteRocketship",
                        "posted_at": posted_at
                    })

        except Exception as e:
            print(f"RemoteRocketship scraper error on page {page}:", e)
            continue

    return jobs

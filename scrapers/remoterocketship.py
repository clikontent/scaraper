import requests
import random
import time
from bs4 import BeautifulSoup
from datetime import datetime, timezone

BASE_URL = "https://www.remoterocketship.com/?page={page}&sort=DateAdded&locations=Africa"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 10)",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

def remoterocketship(max_pages=15):
    jobs = []

    for page in range(1, max_pages + 1):
        url = BASE_URL.format(page=page)

        # --- Rate limit safety delay ---
        time.sleep(random.uniform(2.5, 5.0))

        # --- Retry logic for 429 ---
        for attempt in range(5):
            try:
                response = requests.get(url, headers=get_headers(), timeout=20)

                if response.status_code == 429:
                    wait = (2 ** attempt) + random.random()
                    print(f"429 Too Many Requests on page {page}. Backing off {wait:.2f}s")
                    time.sleep(wait)
                    continue

                response.raise_for_status()
                break  # success, exit retry loop

            except Exception as e:
                if attempt == 4:
                    print(f"RemoteRocketship scraper FAILED on page {page}: {e}")
                    return jobs
                else:
                    wait = (2 ** attempt) + random.random()
                    print(f"Error on page {page}. Retrying in {wait:.2f}s:", e)
                    time.sleep(wait)

        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.select("div.job-listing-item")

        if not job_cards:
            print(f"No more jobs found (page {page}). Stopping.")
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
            location = location_el.get_text(strip=True) if location_el else "Remote"

            # Keep only Africa jobs
            if location and "africa" not in location.lower():
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

    return jobs

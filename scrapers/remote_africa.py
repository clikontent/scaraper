# scrapers/remote_africa_playwright.py

from playwright.async_api import async_playwright
from datetime import datetime, timezone

URL = "https://remoteafrica.io"

async def scrape_remote_africa():
    jobs = []
    now = datetime.now(timezone.utc)

    async with async_playwright() as p:
        # Launch headless browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL)

        # Scroll to load more jobs
        previous_height = None
        while True:
            current_height = await page.evaluate("document.body.scrollHeight")
            if previous_height == current_height:
                break
            previous_height = current_height
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1500)  # wait for jobs to load

        # Select all job cards
        job_cards = await page.query_selector_all("a.job-card__link")

        for card in job_cards:
            try:
                title = await card.query_selector_eval(".job-card__title", "el => el.textContent")
                company = await card.query_selector_eval(".job-card__company", "el => el.textContent")
                href = await card.get_attribute("href")

                if not title or not company or not href:
                    continue

                jobs.append({
                    "external_id": "https://remoteafrica.io" + href,
                    "title": title.strip(),
                    "company": company.strip(),
                    "description": None,
                    "location": "Remote (Africa)",
                    "job_type": None,
                    "salary": None,
                    "experience_level": None,
                    "skills": [],
                    "requirements": [],
                    "posted_date": now,
                    "application_url": "https://remoteafrica.io" + href,
                    "company_logo": None,
                    "source": "RemoteAfrica",
                    "category": None,
                    "raw_data": {
                        "html": await card.inner_html(),
                        "scraped_at": now.isoformat(),
                    },
                })
            except Exception as e:
                print("RemoteAfrica card error:", e)

        await browser.close()

    return jobs

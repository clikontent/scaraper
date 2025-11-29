import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone
# requests is no longer needed

BASE_URL = "https://www.remoterocketship.com/?page={page}&sort=DateAdded&locations=Africa&ref=oscarw5"

async def scrape_remoterocketship(max_pages=15): # <-- Renamed and made async
    """
    Scrape RemoteRocketship jobs filtered by Africa using aiohttp for speed.
    """
    jobs = []

    # Use aiohttp.ClientSession for connection pooling
    async with aiohttp.ClientSession() as session:
        for page in range(1, max_pages + 1):
            url = BASE_URL.format(page=page)

            try:
                # Use await for the asynchronous request
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    response.raise_for_status()
                    
                    # Get the response text asynchronously
                    text = await response.text()
                    soup = BeautifulSoup(text, "html.parser")
                    job_cards = soup.select("div.job-listing-item")

                    # ... (rest of your scraping logic is the same)
                    
                    # Stop when no more jobs
                    if not job_cards:
                        break

                    for card in job_cards:
                        # ... (All job parsing logic remains the same)
                        # ...
                        # ...

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

# Note: You will need to run this function using 'await scrape_remoterocketship()' 
# inside an async context (e.g., in your main script: asyncio.run(scrape_remoterocketship()))

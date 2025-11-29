import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import asyncio
import re

# Base URLs
BASE_URL = "https://www.climatechangecareers.com"
REMOTE_JOBS_URL = BASE_URL + "/jobs/remote/"

def clean_html(html):
    """Convert HTML to clean plain text."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    # Get text, strip and collapse extra whitespace/newlines
    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r'\n\s*\n', r'\n\n', text) # Collapse multiple newlines
    return text.strip()

async def fetch_page(session, url):
    """Helper to safely fetch a page with a User-Agent."""
    try:
        async with session.get(
            url, 
            headers={"User-Agent": "Mozilla/5.0"}, 
            timeout=aiohttp.ClientTimeout(total=15)
        ) as res:
            res.raise_for_status()
            return await res.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

async def scrape_job_description(session, job):
    """Fetches the detail page for a single job to get the description."""
    if not job.get("application_url"):
        return job

    job_page = await fetch_page(session, job["application_url"])
    if not job_page:
        return job

    try:
        job_soup = BeautifulSoup(job_page, "html.parser")
        
        # Adjust selector based on common job site structures
        desc_el = job_soup.select_one(".job-description, .description, #job-content")
        
        description_html = desc_el.decode_contents() if desc_el else ""
        job["description"] = clean_html(description_html)
        
        # Optional: Scrape extra fields if available on detail page
        # e.g., job_type_el = job_soup.select_one(".job-type")
        
    except Exception as e:
        print(f"Error scraping description for {job.get('title')}: {e}")
        
    # Update scraped_at time since we accessed the page
    job["raw_data"]["scraped_at"] = datetime.now(timezone.utc).isoformat()
    return job

async def scrape_climatechangecareers():
    """Main function to scrape job listings."""
    jobs = []
    page_number = 1
    has_next_page = True

    async with aiohttp.ClientSession() as session:
        while has_next_page:
            url = REMOTE_JOBS_URL + f"?page={page_number}"
            print(f"Scraping ClimateChangeCareers page {page_number}...") # Debug print
            
            page_text = await fetch_page(session, url)
            if not page_text:
                break # Stop if page fetch failed

            soup = BeautifulSoup(page_text, "html.parser")

            # **CRITICAL STEP: Inspect HTML to find the correct job card selector**
            job_cards = soup.select("div.job-listing, li.job-listing, a.job-link, .card")
            
            if not job_cards:
                print("No more job cards found. Stopping.")
                break  # No more jobs found

            job_tasks = []
            
            for card in job_cards:
                try:
                    # Initial data extraction from the listing card
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
                    posted_date = datetime.now(timezone.utc)
                    if date_el:
                        date_text = date_el.get_text(strip=True)
                        try:
                            # Use common format that might be found on the site
                            posted_date = datetime.strptime(date_text, "%d %b %Y").replace(tzinfo=timezone.utc)
                        except Exception:
                            pass # Keep posted_date as now if parsing fails

                    if not (title and link): continue # Skip incomplete cards

                    # Create job dict placeholder
                    job = {
                        "external_id": link,
                        "title": title,
                        "company": company,
                        "description": None, # Will be filled by scrape_job_description
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
                        "raw_data": {
                            "html": str(card),
                            "scraped_at": datetime.now(timezone.utc).isoformat(),
                        },
                    }
                    
                    # Add task to fetch description concurrently
                    job_tasks.append(scrape_job_description(session, job))

                except Exception as e:
                    print("Error processing climatechangecareers job card:", e)
                    continue

            # Run all description fetching tasks concurrently
            completed_jobs = await asyncio.gather(*job_tasks)
            jobs.extend(completed_jobs)


            # Check if a "Next" page exists for continuous scraping
            next_page_el = soup.select_one("a.next, .pagination-next")
            
            # Check for a specific 'Next' link href or a link that doesn't point to the current page
            is_next_active = (
                next_page_el and 
                next_page_el.has_attr('href') and 
                f"page={page_number + 1}" in next_page_el['href']
            )

            if is_next_active:
                page_number += 1
            else:
                has_next_page = False

    return jobs

# Example usage (uncomment this block to test the script directly)
# if __name__ == '__main__':
#     # Note: This will execute the scrape and print results if successful
#     results = asyncio.run(scrape_climatechangecareers())
#     print(f"Found {len(results)} jobs from Climate Change Careers.")
#     # for job in results[:5]:
#     #     print(f"- {job['title']} at {job['company']}")

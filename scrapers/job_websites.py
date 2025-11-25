# scrapers/job_websites.py

from .remoteok import scrape_remoteok
from .weworkremotely import scrape_weworkremotely
from .remote_africa import scrape_remote_africa

# List of all scraper functions
SCRAPERS = [
    scrape_remoteok,
    scrape_remote_africa,
    scrape_weworkremotely
]

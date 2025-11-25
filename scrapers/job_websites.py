# scrapers/job_websites.py

from .remoteok import scrape_remoteok
from .myjobmag import scrape_myjobmag
from .brightermonday import scrape_brightermonday
from .beyondthesavannah import scrape_beyondthesavannah
from .indeed import scrape_indeed
from .weworkremotely import scrape_weworkremotely
from .remote_africa import scrape_remote_africa

# List of all scraper functions
SCRAPERS = [
    scrape_remoteok,
    scrape_myjobmag,
    scrape_brightermonday,
    scrape_beyondthesavannah,
    scrape_indeed,
    scrape_remote_africa,
    scrape_weworkremotely
]

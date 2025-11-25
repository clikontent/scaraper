# scrapers/job_websites.py

from .remoteok import scrape_remoteok
from .myjobmag import scrape_myjobmag
from .brightermonday import scrape_brightermonday
from .beyondthesavannah import scrape_beyondthesavannah
from .fuzu import scrape_fuzu
from .weworkremotely import scrape_weworkremotely

# List of all scraper functions
SCRAPERS = [
    scrape_remoteok,
    scrape_myjobmag,
    scrape_brightermonday,
    scrape_beyondthesavannah,
    scrape_indeed,
    scrape_resome_africa,
    scrape_weworkremotely
]

# scrapers/job_websites.py

from .remoteok import scrape_remoteok
from .weworkremotely import scrape_weworkremotely
from .remote_africa import scrape_remote_africa
from .climatechangecareers import scrape_climatechangecareers
from .nodesk import scrape_nodesk
from .remoterocketship import scrape_remoterocketship


# List of all scraper functions
SCRAPERS = [
    scrape_remote_africa,
    scrape_remoteok,
    scrape_weworkremotely,
    scrape_climatechangecareers,
    scrape_nodesk,
    scrape_remoterocketship
    ]







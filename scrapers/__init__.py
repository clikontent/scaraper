from scrapers.remote_africa import scrape_remote_africa
from scrapers.myjobmag import scrape_myjobmag
from scrapers.remoteok import scrape_remoteok
from scrapers.weworkremotely import scrape_weworkremotely
from scrapers.brightermonday import scrape_brightermonday
from scrapers.beyondthesavannah import scrape_beyondthesavannah

SCRAPERS = [
    scrape_remote_africa,
    scrape_myjobmag,
    scrape_remoteok,
    scrape_weworkremotely,
    scrape_brightermonday,
    scrape_beyondthesavannah
]

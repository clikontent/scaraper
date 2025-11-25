# scrapers/weworkremotely.py

import aiohttp
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

RSS_URL = "https://weworkremotely.com/remote-jobs.rss"

async def scrape_weworkremotely():
    jobs = []

    async with aiohttp.ClientSession() as session:
        async with session.get(RSS_URL, headers={"User-Agent": "Mozilla/5.0"}) as res:
            xml_text = await res.text()

    root = ET.fromstring(xml_text)
    
    for item in root.findall(".//item"):
        try:
            title = item.find("title").text.strip() if item.find("title") is not None else None
            link = item.find("link").text.strip() if item.find("link") is not None else None
            company = item.find("author").text.strip() if item.find("author") is not None else None
            description = item.find("description").text.strip() if item.find("description") is not None else None
            pub_date_text = item.find("pubDate").text if item.find("pubDate") is not None else None
            posted_date = datetime.strptime(pub_date_text, "%a, %d %b %Y %H:%M:%S %z") if pub_date_text else datetime.now(timezone.utc)

            job = {
                "external_id": link,
                "title": title,
                "company": company,
                "description": description,
                "location": "Remote (Global)",
                "job_type": None,
                "salary": None,
                "experience_level": None,
                "skills": [],
                "requirements": [],
                "posted_date": posted_date,
                "application_url": link,
                "company_logo": None,
                "source": "WeWorkRemotelyRSS",
                "category": None,
                "raw_data": {
                    "xml": ET.tostring(item, encoding="unicode"),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                },
            }
            jobs.append(job)
        except Exception as e:
            print("WeWorkRemotely RSS error:", e)

    return jobs

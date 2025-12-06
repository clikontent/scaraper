import aiohttp
from datetime import datetime, timezone

API_URL = "https://www.climatechangecareers.com/api/jobs?page={page}&type=remote"

async def scrape_climatechangecareers():
    jobs = []
    page = 1
    more_pages = True

    async with aiohttp.ClientSession() as session:
        while more_pages:
            url = API_URL.format(page=page)
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as res:
                data = await res.json()

            job_list = data.get("jobs", [])
            if not job_list:
                break

            for job in job_list:
                try:
                    job_id = job.get("id")
                    title = job.get("title")
                    company = job.get("company_name")
                    location = job.get("location") or "Remote"
                    posted = job.get("published_at")
                    url = f"https://www.climatechangecareers.com/jobs/{job_id}"

                    posted_date = datetime.fromisoformat(posted).replace(tzinfo=timezone.utc) \
                        if posted else datetime.now(timezone.utc)

                    jobs.append({
                        "external_id": job_id,
                        "title": title,
                        "company": company,
                        "description": job.get("description", ""),
                        "location": location,
                        "job_type": job.get("type"),
                        "salary": job.get("salary"),
                        "experience_level": None,
                        "skills": job.get("skills", []),
                        "requirements": job.get("requirements", []),
                        "posted_date": posted_date,
                        "application_url": url,
                        "company_logo": job.get("company_logo"),
                        "source": "ClimateChangeCareers",
                        "category": job.get("sector"),
                        "raw_data": job,
                    })
                except Exception as e:
                    print("Climate jobs error:", e)

            # API pagination
            more_pages = data.get("has_more", False)
            page += 1

    return jobs

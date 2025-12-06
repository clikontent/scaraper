import aiohttp
from datetime import datetime, timezone

API_URL = "https://nodesk.co/api/jobs/?page={page}"

async def scrape_nodesk(max_pages=5):
    jobs = []
    page = 1

    async with aiohttp.ClientSession() as session:
        while page <= max_pages:
            url = API_URL.format(page=page)
            
            try:
                async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                    resp.raise_for_status()
                    data = await resp.json()

            except Exception as e:
                print("NoDesk error:", e)
                break

            job_list = data.get("results", [])
            if not job_list:
                break

            for j in job_list:
                posted_date = (
                    datetime.fromisoformat(j["pub_date"]).replace(tzinfo=timezone.utc)
                    if "pub_date" in j
                    else datetime.now(timezone.utc)
                )

                job = {
                    "external_id": j.get("id"),
                    "title": j.get("title"),
                    "company": j.get("company"),
                    "description": j.get("description"),
                    "location": j.get("location") or "Remote",
                    "job_type": j.get("employment_type"),
                    "salary": None,
                    "experience_level": None,
                    "skills": j.get("tags", []),
                    "requirements": [],
                    "posted_date": posted_date,
                    "application_url": j.get("apply_url"),
                    "company_logo": j.get("company_logo"),
                    "source": "NoDesk",
                    "category": j.get("categories"),
                    "raw_data": j,
                }

                jobs.append(job)

            # NoDesk pagination
            if not data.get("next"):
                break

            page += 1

    return jobs

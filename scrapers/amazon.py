import requests
from bs4 import BeautifulSoup

API_URL = "https://www.amazon.jobs/en/search.json"
BASE_URL = "https://www.amazon.jobs"


def get_amazon_jobs():

    all_jobs = []
    offset = 0
    limit = 100
    total_jobs = None

    while total_jobs is None or offset < total_jobs:

        params = {
            "offset": offset,
            "result_limit": limit,
            "sort": "recent",
            "country": "IRL"
        }

        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            response.raise_for_status()
            data = response.json()

            total_jobs = data.get("hits", 0)
            jobs = data.get("jobs", [])

            if not jobs:
                break

            all_jobs.extend(jobs)

            print(f"Retrieved {len(all_jobs)} / {total_jobs}")

            offset += limit

        except (requests.exceptions.RequestException, ValueError) as error:
            print("Amazon API error:", error)
            break

    return all_jobs


def normalise_amazon_job(job):

    description = job.get("description", "")
    basic_qualifications = job.get("basic_qualifications", "")
    preferred_qualifications = job.get("preferred_qualifications", "")

    combined_content = f"""
    {description}
    {basic_qualifications}
    {preferred_qualifications}
    """

    clean_content = BeautifulSoup(
        combined_content,
        "html.parser"
    ).get_text(" ", strip=True)

    job_path = job.get("job_path", "")

    job_url = (
        BASE_URL + job_path
        if job_path.startswith("/")
        else job_path
    )

    return {
        "id": f"amazon_{job.get('id_icims')}",
        "title": job.get("title", ""),
        "location": {
            "name": job.get("normalized_location")
            or job.get("location", "")
        },
        "content": clean_content,
        "absolute_url": job_url,
        "company": "Amazon"
    }


def filter_dublin_jobs(jobs):

    dublin_jobs = []

    for job in jobs:

        location = job.get("normalized_location", "")

        if "dublin" in location.lower():
            dublin_jobs.append(normalise_amazon_job(job))

    return dublin_jobs


if __name__ == "__main__":

    jobs = get_amazon_jobs()
    dublin_jobs = filter_dublin_jobs(jobs)


    print("\n========== AMAZON SUMMARY ==========")
    print("Total vacancies:", len(jobs))
    print("Dublin vacancies:", len(dublin_jobs))

    for job in dublin_jobs[:10]:

        print("\n-------------------------")
        print("Title:", job["title"])
        print("Location:", job["location"]["name"])
        print("ID:", job["id"])
        print("URL:", job["absolute_url"])

    print("\n========== AMAZON LOCATION BREAKDOWN ==========")

    locations = {}

    for job in jobs:
        location = job.get("normalized_location", "Unknown")
        locations[location] = locations.get(location, 0) + 1

    for location, count in sorted(locations.items()):
        print(f"{location}: {count}")
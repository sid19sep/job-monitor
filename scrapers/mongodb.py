import requests


API_URL = "https://boards-api.greenhouse.io/v1/boards/mongodb/jobs"


def get_mongodb_jobs():

    params = {"content": "true"}

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        return data.get("jobs", [])

    except requests.exceptions.RequestException as error:

        print(f"MongoDB API error: {error}")
        return []


def filter_dublin_jobs(jobs):

    dublin_jobs = []

    for job in jobs:

        location = job.get("location", {}).get("name", "")

        if "dublin" in location.lower():

            dublin_jobs.append(job)

    return dublin_jobs


if __name__ == "__main__":

    all_jobs = get_mongodb_jobs()

    dublin_jobs = filter_dublin_jobs(all_jobs)

    print(f"Total MongoDB jobs: {len(all_jobs)}")
    print(f"Dublin jobs: {len(dublin_jobs)}")

    for job in dublin_jobs:

        print("\n-----------------------------")
        print("Title:", job.get("title"))
        print("Location:", job.get("location", {}).get("name"))
        print("URL:", job.get("absolute_url"))
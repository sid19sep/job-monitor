import schedule
import time

from scrapers.mongodb import (
    get_mongodb_jobs,
    filter_dublin_jobs as filter_mongodb_dublin_jobs
)

from scrapers.amazon import (
    get_amazon_jobs,
    filter_dublin_jobs as filter_amazon_dublin_jobs
)
from job_matcher import filter_relevant_jobs
from database.job_store import (
    initialize_database,
    save_job,
    get_unnotified_jobs,
    mark_job_notified
)

from notifications.telegram import send_message
from database.job_store import mark_job_notified

def send_job_alert(job):
    company = job.get("company", "MongoDB")

    priority_role = (
        company == "MongoDB"
        and "associate technical services engineer"
        in job["title"].lower()
    )

    if priority_role:
        heading = "🚨 PRIORITY ROLE FOUND!"
    else:
        heading = f"🆕 NEW {company.upper()} VACANCY!"

    message = f"""
{heading}

🏢 Company: {company}
💼 Role: {job['title']}
📍 Location: {job['location']}

⭐ Match Score: {job['score']}/100
🎯 Classification: {job['match_level']}

🔗 Apply here:
{job['url']}
"""

    if send_message(message):
        mark_job_notified(job["id"])

def run_monitor():
    print("\n========== JOB MONITOR ==========")

    initialize_database()

    # MongoDB
    print("\nFetching MongoDB vacancies...")
    mongodb_jobs = get_mongodb_jobs()
    mongodb_dublin = filter_mongodb_dublin_jobs(mongodb_jobs)

    print(f"MongoDB vacancies: {len(mongodb_jobs)}")
    print(f"MongoDB Dublin vacancies: {len(mongodb_dublin)}")

    # Amazon
    print("\nFetching Amazon vacancies...")
    amazon_jobs = get_amazon_jobs()
    amazon_dublin = filter_amazon_dublin_jobs(amazon_jobs)

    print(f"Amazon vacancies: {len(amazon_jobs)}")
    print(f"Amazon Dublin vacancies: {len(amazon_dublin)}")

    # Combine both companies
    all_dublin_jobs = mongodb_dublin + amazon_dublin

    print(f"\nTotal Dublin vacancies: {len(all_dublin_jobs)}")

    # Match relevant jobs
    matches = filter_relevant_jobs(all_dublin_jobs)

    print(f"Relevant vacancies: {len(matches)}")

    # Save new vacancies
    new_jobs = []

    for job in matches:
        if save_job(job):
            new_jobs.append(job)

    # Send notifications for unnotified jobs
    pending_jobs = get_unnotified_jobs()

    for job in pending_jobs:
        job["id"] = job["job_id"]
        send_job_alert(job)

    # Summary
    print("\n========== SUMMARY ==========")
    print(f"Relevant vacancies: {len(matches)}")
    print(f"New vacancies: {len(new_jobs)}")
    print(f"Already tracked: {len(matches) - len(new_jobs)}")
    print(f"Notifications processed: {len(pending_jobs)}")


if __name__ == "__main__":

    print("MongoDB Job Monitor Started!")
    print("Checking for new vacancies every 30 minutes.")

    # Run immediately when started
    run_monitor()

    # Schedule future checks
    schedule.every(30).minutes.do(run_monitor)

    while True:
        schedule.run_pending()
        time.sleep(1)
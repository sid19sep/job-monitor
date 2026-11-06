from scrapers.mongodb import get_mongodb_jobs, filter_dublin_jobs
from job_matcher import filter_relevant_jobs
from database.job_store import initialize_database, save_job

# Initialise database
initialize_database()

# Fetch and filter jobs
jobs = get_mongodb_jobs()
dublin_jobs = filter_dublin_jobs(jobs)
matches = filter_relevant_jobs(dublin_jobs)

new_jobs = 0
existing_jobs = 0

# Store relevant vacancies
for job in matches:
    if save_job(job):
        new_jobs += 1
        print("NEW:", job["title"])
    else:
        existing_jobs += 1
        print("ALREADY STORED:", job["title"])

print("\n========== DATABASE SUMMARY ==========")
print("Relevant vacancies:", len(matches))
print("New vacancies stored:", new_jobs)
print("Already stored:", existing_jobs)
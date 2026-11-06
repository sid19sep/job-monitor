from scrapers.mongodb import get_mongodb_jobs, filter_dublin_jobs
from job_matcher import filter_relevant_jobs


jobs = get_mongodb_jobs()

dublin_jobs = filter_dublin_jobs(jobs)

matches = filter_relevant_jobs(dublin_jobs)


print("\n========== MONGODB JOB MATCHES ==========\n")

for job in matches:

    print("Title:", job["title"])
    print("Location:", job["location"])
    print("Score:", job["score"], "/ 100")
    print("Match:", job["match_level"])
    print("Categories:", job["categories"])
    print("Matched skills:", job["matched_skills"])
    print("URL:", job["url"])

    print("----------------------------------------")


print("\n========== SUMMARY ==========")

print("Total Dublin vacancies:", len(dublin_jobs))
print("Relevant vacancies:", len(matches))
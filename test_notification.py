from main import send_job_alert

test_job = {
    "id": "TEST123",
    "title": "Associate Technical Services Engineer",
    "location": "Dublin, Ireland",
    "url": "https://www.mongodb.com/company/careers/see-jobs",
    "score": 100,
    "match_level": "STRONG"
}

send_job_alert(test_job)
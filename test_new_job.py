import sqlite3

from database.job_store import save_job, mark_job_notified
from notifications.telegram import send_message

test_job = {
    "id": "TEST_AMAZON_20261106_001",
    "title": "Junior AI Engineer - Test Vacancy",
    "company": "Amazon",
    "location": "Dublin, IRL",
    "url": "https://www.amazon.jobs/",
    "score": 85,
    "match_level": "STRONG"
}

try:
    print("Saving simulated vacancy...")

    saved = save_job(test_job)

    if saved:
        print("SUCCESS: New vacancy saved to database.")

        message = f"""
🆕 NEW AMAZON VACANCY!

🏢 Company: Amazon
💼 Role: {test_job['title']}
📍 Location: {test_job['location']}

⭐ Match Score: {test_job['score']}/100
🎯 Classification: {test_job['match_level']}

🔗 Apply here:
{test_job['url']}
"""

        print("\nSending Telegram notification...")

        if send_message(message):
            mark_job_notified(test_job["id"])
            print("SUCCESS: Vacancy marked as notified.")
        else:
            print("Notification failed.")

    else:
        print("Vacancy already exists.")

finally:
    # Remove the temporary test record
    connection = sqlite3.connect("database/jobs.db")
    connection.execute(
        "DELETE FROM jobs WHERE job_id = ?",
        (test_job["id"],)
    )
    connection.commit()
    connection.close()

    print("\nTemporary test record cleaned up.")
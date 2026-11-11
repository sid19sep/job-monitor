import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError


# Select database depending on execution environment
DB_PATH = Path(__file__).parent / "jobs.db"

TABLE_NAME = os.getenv("JOBS_TABLE")

dynamodb_table = None

if TABLE_NAME:
    dynamodb = boto3.resource("dynamodb")
    dynamodb_table = dynamodb.Table(TABLE_NAME)


def initialize_database():

    # AWS DynamoDB table already exists
    if dynamodb_table:
        print("Using AWS DynamoDB.")
        return

    # Local SQLite database
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            url TEXT,
            date_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            score INTEGER,
            match_level TEXT,
            notified INTEGER DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()

    print("Using local SQLite database.")


def job_exists(job_id):

    if dynamodb_table:
        response = dynamodb_table.get_item(
            Key={"job_id": str(job_id)}
        )

        return "Item" in response

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT job_id FROM jobs WHERE job_id = ?",
        (str(job_id),)
    )

    result = cursor.fetchone()
    connection.close()

    return result is not None


def save_job(job):

    if dynamodb_table:

        item = {
            "job_id": str(job["id"]),
            "title": job["title"],
            "company": job.get("company", "MongoDB"),
            "location": job["location"],
            "url": job["url"],
            "date_found": datetime.now(timezone.utc).isoformat(),
            "score": int(job["score"]),
            "match_level": job["match_level"],
            "notified": 0
        }

        try:
            dynamodb_table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(job_id)"
            )

            return True

        except ClientError as error:

            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False

            raise

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO jobs
        (job_id, title, company, location, url, score, match_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        str(job["id"]),
        job["title"],
        job.get("company", "MongoDB"),
        job["location"],
        job["url"],
        job["score"],
        job["match_level"]
    ))

    connection.commit()
    inserted = cursor.rowcount > 0
    connection.close()

    return inserted


def get_unnotified_jobs():

    if dynamodb_table:

        jobs = []
        response = dynamodb_table.scan(
            FilterExpression=Attr("notified").eq(0)
        )

        jobs.extend(response.get("Items", []))

        while "LastEvaluatedKey" in response:

            response = dynamodb_table.scan(
                FilterExpression=Attr("notified").eq(0),
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )

            jobs.extend(response.get("Items", []))

        return jobs

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT job_id, title, company, location, url, score, match_level
        FROM jobs
        WHERE notified = 0
    """)

    jobs = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return jobs


def mark_job_notified(job_id):

    if dynamodb_table:

        dynamodb_table.update_item(
            Key={"job_id": str(job_id)},
            UpdateExpression="SET notified = :value",
            ExpressionAttributeValues={
                ":value": 1
            }
        )

        return

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE jobs
        SET notified = 1
        WHERE job_id = ?
    """, (str(job_id),))

    connection.commit()
    connection.close()


def mark_all_existing_as_notified():

    if dynamodb_table:

        response = dynamodb_table.scan(
            ProjectionExpression="job_id"
        )

        while True:

            for item in response.get("Items", []):
                mark_job_notified(item["job_id"])

            if "LastEvaluatedKey" not in response:
                break

            response = dynamodb_table.scan(
                ProjectionExpression="job_id",
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )

        print("Existing vacancies marked as processed.")
        return

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE jobs
        SET notified = 1
    """)

    connection.commit()
    connection.close()

    print("Existing vacancies marked as processed.")
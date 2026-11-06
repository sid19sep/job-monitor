import re
from config_loader import load_config


def normalise(text):

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def contains_phrase(text, phrase):

    pattern = r"\b" + re.escape(phrase) + r"\b"

    return bool(re.search(pattern, text))


def match_job(job):

    config = load_config()

    categories = config["job_categories"]
    skills = config["relevant_skills"]

    title = normalise(job.get("title", ""))
    description = normalise(job.get("content", ""))

    matched_categories = []
    matched_titles = []
    description_matches = []
    matched_skills = []

    # 1. Check job title against our preferred roles

    for category, keywords in categories.items():

        for keyword in keywords:

            keyword = normalise(keyword)

            if contains_phrase(title, keyword):

                matched_categories.append(category)
                matched_titles.append(keyword)

            elif contains_phrase(description, keyword):

                description_matches.append(category)

    # 2. Check relevant technical skills

    for skill in skills:

        skill = normalise(skill)

        if contains_phrase(description, skill):

            matched_skills.append(skill)

    # Remove duplicate categories

    matched_categories = list(set(matched_categories))
    description_matches = list(set(description_matches))

    # 3. Calculate relevance score

    score = 0

    if contains_phrase(title, "associate technical services engineer"):
        score += 40

    if matched_titles:
        score += 60

    if description_matches:
        score += min(len(description_matches) * 10, 20)

    skill_score = min(len(matched_skills) * 2, 20)

    score += skill_score

    score = min(score, 100)

    # 4. Classify the vacancy

    if score >= 80:
        match_level = "STRONG"

    elif score >= 50:
        match_level = "POTENTIAL"

    elif score >= 30:
        match_level = "REVIEW"

    else:
        match_level = "NOT_RELEVANT"

    return {
        "id": job.get("id"),
        "company": job.get("company", "MongoDB"),
        "title": job.get("title"),
        "location": job.get("location", {}).get("name", ""),
        "url": job.get("absolute_url", ""),
        "score": score,
        "match_level": match_level,
        "categories": matched_categories or description_matches,
        "matched_keywords": matched_titles,
        "matched_skills": matched_skills
    }


def filter_relevant_jobs(jobs):

    relevant_jobs = []

    for job in jobs:

        result = match_job(job)

        if result["match_level"] != "NOT_RELEVANT":

            relevant_jobs.append(result)

    return sorted(
        relevant_jobs,
        key=lambda job: job["score"],
        reverse=True
    )
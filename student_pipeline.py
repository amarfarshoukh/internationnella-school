import pandas as pd
import requests
from datetime import datetime, timedelta

def get_student_info_by_cntstuid(csv_path, cntstuid, chunk_size=100000):
    for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
        student_row = chunk[chunk['CNTSTUID'] == cntstuid]
        if not student_row.empty:
            return student_row.iloc[0]
    return None

def fetch_news(country_code, exam_date, api_key):
    from_date = (datetime.strptime(exam_date, "%Y-%m-%d") - timedelta(days=3)).strftime("%Y-%m-%d")
    to_date = (datetime.strptime(exam_date, "%Y-%m-%d") + timedelta(days=3)).strftime("%Y-%m-%d")

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={country_code}&from={from_date}&to={to_date}&sortBy=popularity&language=en&apiKey={api_key}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        # return titles + descriptions, filter out those without description
        return [article["title"] + ". " + article["description"] for article in articles if article["description"]]
    else:
        return []

def query_phi3(articles, exam_date, country_code, hf_token):
    prompt = (
        f"A student from {country_code} had an exam on {exam_date}.\n"
        f"Here are some news events in {country_code} around that time:\n\n"
    )
    for article in articles[:5]:
        prompt += "- " + article + "\n"

    prompt += "\nCould any of these events have reasonably affected the student's exam performance? Give a short reasoning."

    API_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"
    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        # Hugging Face API response is a list with a dictionary containing "generated_text"
        return response.json()[0].get("generated_text", "No response text found.")
    else:
        return f"Error from Hugging Face API: {response.status_code} – {response.text}"

def analyze_student(csv_path, cntstuid, newsapi_key, hf_token):
    student = get_student_info_by_cntstuid(csv_path, cntstuid)
    if student is None:
        return "Student ID not found."

    # Try multiple cases for grade column
    grade = student.get("grade") or student.get("Grade") or student.get("GRADE")
    if grade is None:
        return "Grade data missing."

    # If grade >=16, no detailed message needed
    if grade >= 16:
        return ""

    country = student["CNT"]
    exam_date = student["ExamDate"]

    news_articles = fetch_news(country, exam_date, newsapi_key)
    if not news_articles:
        return "No news found for this date and country."

    phi3_response = query_phi3(news_articles, exam_date, country, hf_token)
    return phi3_response

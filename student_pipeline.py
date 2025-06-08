import pandas as pd
import requests
from datetime import datetime, timedelta

def get_student_info_by_cntstuid(csv_path, cntstuid, chunk_size=100000):
    """Find student record by ID (handles float IDs)"""
    try:
        search_id = float(cntstuid)
    except ValueError:
        return None

    for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
        id_cols = [col for col in chunk.columns if 'id' in col.lower()]
        for col in id_cols:
            try:
                student_row = chunk[chunk[col].astype(float) == search_id]
            except ValueError:
                continue
            if not student_row.empty:
                return student_row.iloc[0].to_dict()
    return None

def fetch_news(country, exam_date, api_key):
    """Fetch news articles from NewsAPI for a given country and date"""
    try:
        dt = datetime.strptime(exam_date, "%Y-%m-%d")
    except Exception:
        return []
    from_date = (dt - timedelta(days=3)).strftime("%Y-%m-%d")
    to_date = (dt + timedelta(days=3)).strftime("%Y-%m-%d")
    url = (
    "https://newsapi.org/v2/everything"
    "?q=ALB"
    "&from=2025-06-01"# assuming today is 2025-06-06, this is within the last 30 days
    "&to=2025-06-06"
    "&sortBy=publishedAt"
    "&language=en"
    f"&apiKey=9681360b2f5f452cb6ea040341e58943"
)

    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        return [f"{a.get('title', '')}. {a.get('description', '')}" for a in articles if a.get("description")]
    except Exception as e:
        print(f"NewsAPI Error: {str(e)}")
        return []

def query_phi3_locally(articles, exam_date, country):
    """Query local Phi-3 model via Ollama"""
    prompt = (
        f"A student from {country} had an exam on {exam_date}.\n"
        f"Relevant news around that time:\n\n" +
        "\n".join(f"- {article}" for article in articles[:5]) +
        "\n\nCould these events have affected exam performance? Keep response under 100 words."
    )
    try:
        response = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={
                "model": "phi3:mini",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7}
            }
        )
        return response.json().get("response", "No response generated")
    except Exception as e:
        return f"Phi-3 Error: {str(e)}"

def analyze_student(csv_path, cntstuid, newsapi_key):
    """Main analysis pipeline"""
    student = get_student_info_by_cntstuid(csv_path, cntstuid)
    if student is None:
        return (
            f"Student ID {cntstuid} not found. Please check:\n"
            f"- ID exists in dataset\n"
            f"- Try numeric format (800001) or string ('800001')"
        )
    # Grade handling
    grade = None
    for k in ["grade", "Grade", "GRADE"]:
        if k in student:
            try:
                grade = float(student[k])
                break
            except Exception:
                pass
    if grade is None:
        return "Grade data missing or not numeric."
    if grade >= 16:
        return ""  # No analysis needed

    country = student.get("CNT", "Unknown")
    exam_date = student.get("ExamDate", "")
    if not exam_date or not country:
        return "Missing exam date or country info."
    news_articles = fetch_news(country, exam_date, newsapi_key)
    if not news_articles:
        return "No relevant news found."
    return query_phi3_locally(news_articles, exam_date, country)
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=30.0
)


def analyze_news(news_items):

    if not news_items:
        return "No recent news signals found."

    headlines = []

    for item in news_items:
        headlines.append(
            f"- {item['title']}"
        )

    prompt = f"""
Analyze these company news headlines.

News:
{chr(10).join(headlines)}

Return:
1. Key developments
2. Business impact
3. One short executive summary
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as exc:
        print("NEWS AI ERROR:", exc)
        return "News analysis unavailable because AI analysis failed."

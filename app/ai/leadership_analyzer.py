import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=30.0
)


def extract_leadership(
    company_name,
    about_page_text=None
):

    if about_page_text is None:
        about_page_text = company_name
        company_name = ""

    prompt = f"""
You are a competitive intelligence analyst.

Company:
{company_name}

About page text:
{about_page_text}

Extract only real leadership people.

Return JSON array:

[
  {{
    "name": "...",
    "role": "CEO"
  }}
]

Rules:
- Ignore navigation text
- Ignore headings
- Ignore marketing content
- Ignore article titles, customer stories, case studies, product names, and page headlines
- Only include names that look like real human first name + last name
- Return only real people
- Maximum 20 people
- Return valid JSON only
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
    except Exception as exc:
        print("LEADERSHIP AI ERROR:", exc)
        return []

    content = (
        response.choices[0]
        .message.content
        .strip()
    )

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        leadership = json.loads(content)
    except json.JSONDecodeError:
        return []

    if not isinstance(leadership, list):
        return []

    people = []

    for person in leadership:

        if not isinstance(person, dict):
            continue

        name = person.get("name")
        role = person.get("role")

        if not name or not role:
            continue

        people.append({
            "name": str(name).strip(),
            "role": str(role).strip()
        })

    return people[:20]

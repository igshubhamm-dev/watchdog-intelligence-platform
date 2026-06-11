import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=30.0
)


def discover_competitors(
    company_name,
    description
):

    prompt = f"""
You are a competitive intelligence analyst.

Company:
{company_name}

Description:
{description}

Identify the top 5 direct competitors.

Rules:
- Return only company names
- One competitor per line
- No numbering
- No explanations
- Do not return the input company itself
- Do not return product names, categories, blogs, or article titles
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
        print("COMPETITOR AI ERROR:", exc)
        return []

    content = (
        response.choices[0]
        .message.content
    )

    competitors = []

    for line in content.split("\n"):

        line = (
            line.replace("-", "")
            .replace("•", "")
            .strip()
        )

        if line:
            competitors.append(line)

    return competitors[:5]

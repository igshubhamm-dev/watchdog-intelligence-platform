import os
import json

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=30.0
)


def generate_brief(summary_text, company_name=None):

    if (
        not summary_text
        or (
            isinstance(summary_text, str)
            and "No recent news signals found" in summary_text
        )
    ):
        return (
            "No executive briefing available because "
            "no recent news signals were found."
        )

    if isinstance(summary_text, dict):
        prompt = f"""
You are a competitive intelligence analyst.

Given the following signal summaries for {company_name or "the company"}, write a concise daily briefing that:
1. highlights the top 3-5 things that changed since yesterday,
2. identifies any patterns or trends across categories,
3. flags any signals that suggest a strategic shift, and
4. provides a one-paragraph executive summary a CEO could read in 30 seconds.

Use only the facts present in these summaries. Do not invent missing signals.

Signal summaries:
{json.dumps(summary_text, ensure_ascii=True)[:20000]}
"""
    else:
        prompt = f"""
You are a competitive intelligence analyst.

Using the following intelligence summary:

{summary_text}

Generate a professional executive briefing with:

1. Executive Summary
2. Key Developments
3. Business Impact
4. Risks
5. Opportunities
6. Recommended Actions

Keep it concise and professional.
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
        print("BRIEFING AI ERROR:", exc)
        return "Executive briefing unavailable because briefing generation failed."

import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=30.0,
)


def empty_summary(category):
    return {
        "category": category,
        "signals_changed": False,
        "key_changes": [],
        "narrative": "No public signal data was available for this category.",
        "so_what": "No competitive implication can be determined from available public data.",
    }


def distill_signal(category, raw_data, previous_summary=None):
    if not raw_data:
        return empty_summary(category)

    prompt = f"""
You are a competitive intelligence analyst.

Signal category:
{category}

Current raw data:
{json.dumps(raw_data, ensure_ascii=True)[:20000]}

Previous summary:
{json.dumps(previous_summary or {}, ensure_ascii=True)[:8000]}

Return valid JSON only with exactly these fields:
- category: string
- signals_changed: boolean
- key_changes: array of strings
- narrative: 2-4 plain-English sentences grounded only in current raw data
- so_what: one sentence explaining the competitive implication

Rules:
- Do not invent facts.
- Do not infer unsupported names, spend, titles, dates, or platforms.
- If the raw data is insufficient, return signals_changed false and an empty key_changes array.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(content)
    except Exception as exc:
        print("SIGNAL DISTILLATION ERROR:", exc)
        return empty_summary(category)

    if not isinstance(parsed, dict):
        return empty_summary(category)

    return {
        "category": str(parsed.get("category") or category),
        "signals_changed": bool(parsed.get("signals_changed")),
        "key_changes": parsed.get("key_changes") if isinstance(parsed.get("key_changes"), list) else [],
        "narrative": str(parsed.get("narrative") or ""),
        "so_what": str(parsed.get("so_what") or ""),
    }

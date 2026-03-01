import os
import json
import requests
import wikipediaapi
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

load_dotenv()

app = FastAPI(title="DoomDive")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

WIKI_API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "doomdive/0.1 (poc)"


def get_random_title() -> str:
    """Return the title of a random English Wikipedia article."""
    resp = requests.get(
        WIKI_API,
        params={
            "action": "query",
            "list": "random",
            "rnnamespace": 0,
            "rnlimit": 1,
            "format": "json",
        },
        headers={"User-Agent": USER_AGENT},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["query"]["random"][0]["title"]


def get_article_text(title: str) -> str:
    """Fetch the full text of a Wikipedia article and return up to 3000 words."""
    wiki = wikipediaapi.Wikipedia(language="en", user_agent=USER_AGENT)
    page = wiki.page(title)
    if not page.exists():
        raise ValueError(f"Page not found: {title}")
    words = page.text.split()
    return " ".join(words[:3000])


@app.get("/dive")
def dive():
    """Fetch a random Wikipedia article and return a GPT-generated summary and interesting facts."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, detail="OPENAI_API_KEY not configured")

    try:
        title = get_random_title()
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Failed to fetch random article: {e}") from e

    try:
        text = get_article_text(title)
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Failed to fetch article text: {e}") from e

    prompt = (
        "You are an enthusiastic encyclopedia assistant. "
        "Read the following Wikipedia article and return ONLY valid JSON (no markdown, no code fences) with exactly these keys:\n"
        '  "title": the article title (string),\n'
        '  "summary": a 2-3 sentence overview (string),\n'
        '  "interesting_facts": a list of 3-5 concise interesting highlights (array of strings).\n\n'
        f"Article title: {title}\n\n"
        f"Article text:\n{text}"
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        raw = completion.choices[0].message.content.strip()
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=502, detail=f"GPT returned invalid JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OpenAI API error: {e}")

    return result

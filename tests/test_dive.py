from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.fixture
def mock_random_title():
    """Patch get_random_title to return a fixed article title."""
    with patch("routers.dive.get_random_title", return_value="Python (programming language)") as m:
        yield m


def test_dive_returns_200(mock_random_title):
    """GET /dive returns HTTP 200."""
    resp = client.get("/dive")
    assert resp.status_code == 200


def test_dive_response_shape(mock_random_title):
    """Response contains title, summary, and interesting_facts keys."""
    resp = client.get("/dive")
    data = resp.json()
    assert "title" in data
    assert "summary" in data
    assert "interesting_facts" in data


def test_dive_title_matches_article(mock_random_title):
    """title in response matches the random article title."""
    resp = client.get("/dive")
    assert resp.json()["title"] == "Python (programming language)"


def test_dive_interesting_facts_is_list(mock_random_title):
    """interesting_facts is a non-empty list of strings."""
    facts = client.get("/dive").json()["interesting_facts"]
    assert isinstance(facts, list)
    assert len(facts) > 0
    assert all(isinstance(f, str) for f in facts)


def test_dive_summary_is_string(mock_random_title):
    """summary is a non-empty string."""
    summary = client.get("/dive").json()["summary"]
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_dive_502_on_wiki_failure():
    """GET /dive returns 502 when the Wikipedia API call fails."""
    with patch("routers.dive.get_random_title", side_effect=Exception("network error")):
        resp = client.get("/dive")
    assert resp.status_code == 502
    assert "Failed to fetch random article" in resp.json()["detail"]

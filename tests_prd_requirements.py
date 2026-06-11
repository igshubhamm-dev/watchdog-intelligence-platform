import unittest
from unittest.mock import Mock
from unittest.mock import patch

from app.crawlers.reddit_scraper import scrape_reddit_mentions
from app.crawlers.tech_stack_scraper import detect_tech_stack
from app.crawlers.wikipedia_scraper import scrape_wikipedia_snapshot
from app.services.data_quality import is_valid_job_title
from app.services.data_quality import is_valid_person_name


class PRDRequirementTests(unittest.TestCase):
    def test_job_validation_rejects_navigation_and_ai_titles(self):
        self.assertFalse(is_valid_job_title("Products"))
        self.assertFalse(is_valid_job_title("AI Engineer"))
        self.assertTrue(is_valid_job_title("Product Manager"))

    def test_person_validation_rejects_marketing_content(self):
        self.assertFalse(is_valid_person_name("Customer Story Acme Bank"))
        self.assertFalse(is_valid_person_name("How AI Is Changing Banking"))
        self.assertTrue(is_valid_person_name("Jane Doe"))

    @patch("app.crawlers.reddit_scraper.get_url")
    def test_reddit_scraper_uses_public_json_and_normalizes_mentions(self, get_url):
        response = Mock()
        response.json.return_value = {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "Brand mention",
                            "permalink": "/r/test/comments/abc/brand/",
                            "author": "analyst",
                            "score": 7,
                            "created_utc": 123,
                        }
                    }
                ]
            }
        }
        get_url.return_value = response

        mentions = scrape_reddit_mentions("Acme")

        self.assertEqual(len(mentions), 1)
        self.assertEqual(mentions[0]["source"], "reddit")
        self.assertIn("old.reddit.com", mentions[0]["url"])

    @patch("app.crawlers.wikipedia_scraper.get_url")
    def test_wikipedia_scraper_uses_mediawiki_api(self, get_url):
        search_response = Mock()
        search_response.json.return_value = {
            "query": {
                "search": [
                    {
                        "pageid": 10,
                        "title": "Acme Inc",
                    }
                ]
            }
        }
        page_response = Mock()
        page_response.json.return_value = {
            "query": {
                "pages": {
                    "10": {
                        "fullurl": "https://en.wikipedia.org/wiki/Acme_Inc",
                        "extract": "Public encyclopedia summary.",
                        "revisions": [
                            {
                                "revid": 99,
                                "timestamp": "2026-06-01T00:00:00Z",
                            }
                        ],
                    }
                }
            }
        }
        get_url.side_effect = [search_response, page_response]

        snapshots = scrape_wikipedia_snapshot("Acme")

        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0]["page_id"], "10")
        self.assertEqual(snapshots[0]["revision_id"], "99")

    @patch("app.crawlers.tech_stack_scraper.get_url")
    def test_tech_stack_scraper_extracts_evidence_not_hardcoded_stack(self, get_url):
        response = Mock()
        response.text = """
        <html>
          <head>
            <meta name="generator" content="CMS From Page" />
            <script src="https://cdn.example.com/app.js"></script>
            <link rel="stylesheet" href="/site.css" />
          </head>
        </html>
        """
        get_url.return_value = response

        snapshot = detect_tech_stack("https://example.com")

        values = {item["value"] for item in snapshot["technologies"]}
        self.assertIn("CMS From Page", values)
        self.assertIn("cdn.example.com", values)
        self.assertIn("example.com", values)


if __name__ == "__main__":
    unittest.main()

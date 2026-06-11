from app.crawlers.context_graph_builder import (
    build_context_graph
)

from app.crawlers.job_scraper import (
    scrape_jobs
)

graph = build_context_graph(
    "https://stripe.com"
)

jobs = scrape_jobs(
    graph["careers_page"]
)

print(jobs[:10])
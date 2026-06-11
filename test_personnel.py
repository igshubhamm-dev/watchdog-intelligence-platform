from app.crawlers.context_graph_builder import (
    build_context_graph
)

from app.crawlers.personnel_scraper import (
    scrape_personnel
)

graph = build_context_graph(
    "https://stripe.com"
)

print(
    graph["about_page"]
)

people = scrape_personnel(
    graph["about_page"]
)

print(people)
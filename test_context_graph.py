from app.crawlers.context_graph_builder import build_context_graph

result = build_context_graph(
    "https://stripe.com"
)

print(result)
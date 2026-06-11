from app.crawlers.context_graph_builder import build_context_graph
from app.services.company_service import save_company


url = "https://openai.com"

context_graph = build_context_graph(url)

company = save_company(
    url=url,
    context_graph=context_graph
)

print("Company Saved")
print("ID:", company.id)
print("Name:", company.name)
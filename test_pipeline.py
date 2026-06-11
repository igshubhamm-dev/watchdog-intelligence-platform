from app.services.intelligence_pipeline import (
    analyze_company_pipeline
)

result = analyze_company_pipeline(
    "https://stripe.com"
)

print(result)
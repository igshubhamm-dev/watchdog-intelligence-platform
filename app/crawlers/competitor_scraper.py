def scrape_competitors(company_name):

    competitor_map = {

        "openai": [
            "Anthropic",
            "Google DeepMind",
            "Perplexity",
            "Cohere",
            "Mistral"
        ],

        "figma": [
            "Canva",
            "Sketch",
            "Adobe XD",
            "Framer"
        ],

        "stripe": [
            "PayPal",
            "Adyen",
            "Square",
            "Razorpay"
        ],

        "flipkart": [
            "Amazon",
            "Meesho",
            "Snapdeal"
        ]
    }

    company_name = (
        company_name.lower()
        .split(":")[0]
        .split("|")[0]
        .strip()
    )

    return competitor_map.get(
        company_name,
        []
    )
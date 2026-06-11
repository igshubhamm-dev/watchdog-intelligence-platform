def scrape_glassdoor_reviews(company_name):
    return []


def scrape_google_maps_reviews(company_name):
    return []


def scrape_reviews(company_name):
    reviews = []
    reviews.extend(scrape_glassdoor_reviews(company_name))
    reviews.extend(scrape_google_maps_reviews(company_name))
    return reviews

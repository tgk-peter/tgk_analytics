"""functions to back up Shopify data"""
# package imports
import json
import pandas as pd
import requests
import time

# local imports
from config import settings


def list_endpoint_records(resource):
    """List all records from endpoint and store as JSON

    Keyword arguments:
    endpoint - the target Shopify endpoint
    resource_name - resource is json key name

    Reference:
    https://shopify.dev/docs/api/admin-rest
    """
    # Set URL
    headers = {
        "X-Shopify-Access-Token": settings.shopify_access_token,
        "Content-Type": "application/json"
    }
    payload = {
        "limit": 250,
        #"created_at_min": "2023-01-18"
    }
    shop = "the-good-kitchen-esc.myshopify.com"
    url = f"https://{shop}/admin/api/2023-01/{resource}.json"

    # Access and store first page of results
    session = requests.Session()
    print(f"Get Page 1 of {resource}")
    response = session.get(url, headers=headers, params=payload)
    response_data = response.json()
    all_records = response_data[resource]

    # While Next Link is present, access and store next page
    count = 1
    while "next" in response.links:
        next_url = response.links["next"]["url"]
        response = session.get(next_url, headers=headers)
        count += 1
        print(f"Get Page {count} of {resource}")
        response_data = response.json()
        all_records.extend(response_data[resource])
        # Sleep to avoid rate limit if approach bucket size
        if response.headers["X-Shopify-Shop-Api-Call-Limit"] == "79/80":
            time.sleep(0.25)
    backup_path = f"backups/{resource}.json"
    with open(backup_path, "w") as f:
        json.dump(all_records, f)

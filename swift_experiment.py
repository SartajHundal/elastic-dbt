import requests
import json
from elasticsearch import Elasticsearch

# SWIFT gpi API endpoint
SWIFT_GPI_API_URL = "https://api.swift.com/v1/gpi/tracker"

# Elasticsearch settings
ELASTICSEARCH_HOST = "localhost"
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_INDEX = "swift_transactions"

# API authentication credentials
SWIFT_API_KEY = "your_swift_api_key"
SWIFT_API_SECRET = "your_swift_api_secret"

# Initialize Elasticsearch client
es = Elasticsearch([{"host": ELASTICSEARCH_HOST, "port": ELASTICSEARCH_PORT}])

def fetch_swift_transactions():
    headers = {
        "Authorization": f"Bearer {SWIFT_API_KEY}:{SWIFT_API_SECRET}",
        "Content-Type": "application/json"
    }
    
    # Make request to SWIFT gpi API to retrieve transactions
    response = requests.get(SWIFT_GPI_API_URL, headers=headers)
    
    if response.status_code == 200:
        # Parse JSON response
        transactions = response.json()
        
        # Store transactions in Elasticsearch
        for transaction in transactions:
            # Index transaction data in Elasticsearch
            es.index(index=ELASTICSEARCH_INDEX, body=transaction)
        
        print(f"{len(transactions)} transactions indexed in Elasticsearch.")
    else:
        print(f"Failed to fetch transactions. Status code: {response.status_code}")

if __name__ == "__main__":
    fetch_swift_transactions()

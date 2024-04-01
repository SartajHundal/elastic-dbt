import requests
from elasticsearch import Elasticsearch, helpers

# SWIFT gpi API endpoint
SWIFT_GPI_API_URL = "https://api.swift.com/v1/gpi/tracker"

# API authentication credentials
SWIFT_API_KEY = "your_swift_api_key"
SWIFT_API_SECRET = "your_swift_api_secret"

def initialize_elasticsearch(host="localhost", port=9200):
    """
    Initialize Elasticsearch client with user-defined host and port.

    Parameters:
    - host (str): The hostname of the Elasticsearch instance.
    - port (int): The port number of the Elasticsearch instance.

    Returns:
    - Elasticsearch: An instance of the Elasticsearch client.
    """
    es = Elasticsearch([{"host": host, "port": port}])
    return es

def fetch_swift_transactions(es, index_name="swift_transactions"):
    """
    Fetch SWIFT transactions and index them into Elasticsearch.

    Parameters:
    - es (Elasticsearch): An instance of the Elasticsearch client.
    - index_name (str): The name of the Elasticsearch index to use.
    """
    headers = {
        "Authorization": f"Bearer {SWIFT_API_KEY}:{SWIFT_API_SECRET}",
        "Content-Type": "application/json"
    }
    
    try:
        # Make request to SWIFT gpi API to retrieve transactions
        response = requests.get(SWIFT_GPI_API_URL, headers=headers)
        response.raise_for_status() # Raises an HTTPError if the response status code is not 200
        
        # Parse JSON response
        transactions = response.json()
        
        # Prepare bulk actions for Elasticsearch
        actions = [
            {
                "_index": index_name,
                "_source": transaction
            }
            for transaction in transactions
        ]
        
        # Use helpers.bulk to perform bulk indexing
        helpers.bulk(es, actions)
        
        print(f"{len(transactions)} transactions indexed in Elasticsearch.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch transactions. Error: {e}")

if __name__ == "__main__":
    # Example usage: Pass host and port as arguments
    es = initialize_elasticsearch(host="your_host", port=your_port)
    fetch_swift_transactions(es, index_name="your_index_name")

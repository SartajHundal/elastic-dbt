import logging
import requests
from elasticsearch import Elasticsearch, helpers
from backoff import on_exception, expo

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def check_elasticsearch_health(es):
    """
    Check the health of the Elasticsearch cluster.

    Parameters:
    - es (Elasticsearch): An instance of the Elasticsearch client.

    Returns:
    - str: The health status of the cluster.
    """
    health = es.cluster.health()
    return health['status']

def fetch_swift_transactions(es, 
                             api_url,
                             api_key,
                             api_secret,
                             index_name="swift_transactions"):
    """
    Fetches SWIFT transactions and indexes them into Elasticsearch.

    Parameters:
    - es (Elasticsearch): An instance of the Elasticsearch client.
    - api_url (str): The URL of the SWIFT API.
    - api_key (str): The SWIFT API key.
    - api_secret (str): The SWIFT API secret.
    - index_name (str): The name of the Elasticsearch index to use.
    """
    headers = {
        "Authorization": f"Bearer {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        transactions = response.json()
        actions = [{"_index": index_name, "_source": transaction} for transaction in transactions]
        bulk_index_with_retry(es, actions, index_name)
        print(f"{len(transactions)} transactions indexed in Elasticsearch.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch transactions. Error: {e}")


@on_exception(expo, (requests.exceptions.RequestException,), max_tries=8)
def bulk_index_with_retry(es, actions, index_name):
    """
    Bulk index documents with retry logic.

    Parameters:
    - es (Elasticsearch): An instance of the Elasticsearch client.
    - actions (list): A list of actions to perform.
    - index_name (str): The name of the Elasticsearch index to use.
    """
    helpers.bulk(es, actions)

if __name__ == "__main__":
    es = initialize_elasticsearch(host="your_host", port=your_port)
    fetch_swift_transactions(es, index_name="your_index_name")

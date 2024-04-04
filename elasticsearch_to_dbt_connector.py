import json
from elasticsearch import Elasticsearch
import dbt.clients
import yaml

def load_configuration(filename):
    """Load configuration from YAML file."""
    with open(filename, 'r') as file:
        return yaml.safe_load(file)

def connect_to_elasticsearch(config):
    """Establish connection to Elasticsearch."""
    return Elasticsearch(hosts=config['elasticsearch']['hosts'])

def execute_elasticsearch_query(es_client, config):
    """
    Execute Elasticsearch query and perform routine checks on the returner payload.

    Args:
        es_client: Elasticsearch client.
        config: Configuration dictionary.

    Returns:
        Transformed data.
    """
    response = es_client.search(index=config['elasticsearch']['index_name'], body={"query": {"match_all": {}}})
    
    # Perform routine checks on the returner payload
    if config['routine_checks']['debug_returner_payload']:
        check_returner_payload(response)
    
    return response['hits']['hits']

def check_returner_payload(response):
    """Perform routine checks on the returner payload."""
    # Example checks:
    if 'took' in response:
        print(f"Elasticsearch query took: {response['took']} milliseconds")
    if 'timed_out' in response:
        print(f"Elasticsearch query timed out: {response['timed_out']}")

def transform_data(hits):
    """Transform data from Elasticsearch response."""
    transformed_data = []
    for hit in hits:
        source = hit['_source']
        # Perform any necessary transformations here
        transformed_data.append(source)
    return transformed_data

def insert_data_into_dbt(dbt_client, transformed_data, target):
    """Insert transformed data into dbt-compatible data store."""
    with dbt_client.target(target).create_connection() as connection:
        with connection.handle as handle:
            for record in transformed_data:
                handle.execute("INSERT INTO your_table_name VALUES (%s)", (json.dumps(record),))

def main():
    # Load configuration from YAML file
    config = load_configuration('config.yaml')

    # Initialize Elasticsearch client
    es_client = connect_to_elasticsearch(config)

    # Execute Elasticsearch query
    hits = execute_elasticsearch_query(es_client, config)

    # Transform data
    transformed_data = transform_data(hits)

    # Initialize dbt client
    dbt_client = dbt.clients.profiles.Profile.get_current_profile().get_handle()

    # Insert data into dbt-compatible data store
    insert_data_into_dbt(dbt_client, transformed_data, config['dbt']['target'])

if __name__ == "__main__":
    main()

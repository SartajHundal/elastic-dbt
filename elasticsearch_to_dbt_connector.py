import json
from elasticsearch import Elasticsearch
import dbt.clients
import yaml
import logging

import update_config

def load_configuration(filename):
    """Load configuration from YAML file."""
    with open(filename, 'r') as file:
        return yaml.safe_load(file)

def connect_to_elasticsearch(config):
    """Establish connection to Elasticsearch."""
    return Elasticsearch(hosts=config['elasticsearch']['hosts'])

def execute_elasticsearch_query(es_client, config, batch_size=100):
    """
    Execute Elasticsearch query in batches and yield results.
    
    Args:
        es_client: Elasticsearch client instance.
        config: Configuration dictionary.
        batch_size: Number of documents to retrieve per batch.
    
    Yields:
        List of document hits in batches.
    """
    query = {
        "size": batch_size,
        "query": {"match_all": {}},
        "_source": True  # Retrieve full document content
    }
    page = es_client.search(**config['elasticsearch']['index_name'], body=query)
    while page['hits']['total']['value'] > 0:
        yield page['hits']['hits']
        page = es_client.search_scroll(page['_scroll_id'], scroll='1m', size=batch_size)

def check_returner_payload(response):
    """Perform routine checks on the returner payload."""
    # Example checks:
    if 'took' in response:
        print(f"Elasticsearch query took: {response['took']} milliseconds")
    if 'timed_out' in response:
        print(f"Elasticsearch query timed out: {response['timed_out']}")

def transform_data(batch_generator):
    """
    Transform data from Elasticsearch response batches.
    
    Args:
        batch_generator: Generator yielding Elasticsearch response batches.
    
    Yields:
        Transformed data records.
    """
    for batch in batch_generator:
        for hit in batch:
            source = hit['_source']
            # Perform any necessary transformations here
            yield source

def insert_data_into_dbt(dbt_client, transformed_data, target):
    """Insert transformed data into dbt-compatible data store."""
    with dbt_client.target(target).create_connection() as connection:
        with connection.handle as handle:
            for record in transformed_data:
                handle.execute("INSERT INTO your_table_name VALUES (%s)", (json.dumps(record),))

def main():
    try:
        # Load configuration from YAML file
        config = load_configuration('config.yaml')

        # Initialize Elasticsearch client
        es_client = connect_to_elasticsearch(config)

        # Execute Elasticsearch query in batches
        batch_generator = execute_elasticsearch_query(es_client, config)
        
        # Transform data
        transformed_data_generator = transform_data(batch_generator)

        # Initialize dbt client
        dbt_client = dbt.clients.profiles.Profile.get_current_profile().get_handle()

        # Insert data into dbt-compatible data store
        for transformed_data_batch in transformed_data_generator:
            insert_data_into_dbt(dbt_client, transformed_data_batch, config['dbt']['target'])

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()

    update_config.update_config_value('config.yaml', 'elasticsearch', 'version', '7.15.0')

    # Set up logging
    logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

    # Example usage
    logging.debug('This is a debug message')
    logging.info('This is an informational message')
    logging.warning('This is a warning message')
    logging.error('This is an error message')
    logging.critical('This is a critical message')

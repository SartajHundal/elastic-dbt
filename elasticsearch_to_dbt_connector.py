import json
from elasticsearch import Elasticsearch
import dbt.clients

# Elasticsearch configuration
ELASTICSEARCH_HOST = 'localhost'
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_INDEX = 'your_index_name'
ELASTICSEARCH_QUERY = {
    "query": {
        "match_all": {}
    }
}

# dbt configuration
DBT_PROFILES_DIR = '/path/to/your/dbt/profiles'
TARGET = 'your_dbt_target_name'

# Initialize Elasticsearch client
es_client = Elasticsearch([{'host': ELASTICSEARCH_HOST, 'port': ELASTICSEARCH_PORT}])

# Execute Elasticsearch query
response = es_client.search(index=ELASTICSEARCH_INDEX, body=ELASTICSEARCH_QUERY)

# Extract data from Elasticsearch response
hits = response['hits']['hits']
transformed_data = []

for hit in hits:
    source = hit['_source']
    # Perform any necessary transformations here
    transformed_data.append(source)

# Initialize dbt client
dbt_client = dbt.clients.profiles.Profile.get_current_profile().get_handle()

# Load transformed data into dbt-compatible data store
with dbt_client.target(TARGET).create_connection() as connection:
    with connection.handle as handle:
        for record in transformed_data:
            # Insert data into target table
            # Replace 'your_table_name' with the actual table name in your dbt models
            handle.execute("INSERT INTO your_table_name VALUES (%s)", (json.dumps(record),))

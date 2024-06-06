import yaml

def update_elasticsearch_versions(yaml_file_path, new_version):
    """
    Update the Elasticsearch version in a YAML configuration file.

    Parameters:
    - yaml_file_path (str): The path to the YAML configuration file.
    - new_version (str): The new version of Elasticsearch to update to.
    """
    with open(yaml_file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)
    
    if 'elasticsearch' in yaml_data and 'version' in yaml_data['elasticsearch']:
        yaml_data['elasticsearch']['version'] = new_version
    else:
        yaml_data['elasticsearch'] = {'version': new_version}
    
    with open(yaml_file_path, 'w') as file:
        yaml.safe_dump(yaml_data, file)

# Example usage:
yaml_file_path = 'config.yaml'
new_version = '7.15.0'  # Update this to the desired version
update_elasticsearch_versions(yaml_file_path, new_version)

import yaml

def update_config_value(file_path, section, key, new_value):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    
    if section in config and key in config[section]:
        config[section][key] = new_value
    else:
        config[section] = {key: new_value}
    
    with open(file_path, 'w') as file:
        yaml.safe_dump(config, file)
        

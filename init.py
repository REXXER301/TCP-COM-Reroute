import json
import os
from tcp_server import start_server

CONFIG_PATH = "config.json"

# Define default config
DEFAULT_CONFIG = {
    "left_glove_ip": "0.0.0.0",
    "left_glove_com_port": "COM8",  # or "/dev/ttyUSB0" on Linux
    "right_glove_ip": "0.0.0.0",
    "right_glove_com_port": "COM9",  # or "/dev/ttyUSB2" on Linux
    "host_ip": "127.0.0.1",
    "tcp_port": 65432, # Port to listen on (non-privileged ports are > 1023)
    "baud_rate": 9600
}

def load_config(path=CONFIG_PATH, defaults=DEFAULT_CONFIG):
    # If config doesn't exist, create it
    if not os.path.exists(path):
        print(f"Config not found. Creating default config at '{path}'")
        with open(path, 'w') as f:
            json.dump(defaults, f, indent=4)
        return defaults, True

    # Load existing config
    with open(path, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            print(f"Invalid JSON in '{path}', recreating with defaults.")
            with open(path, 'w') as f:
                json.dump(defaults, f, indent=4)
            return defaults, False

    # Fill in any missing keys with defaults
    updated = False
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
            updated = True

    # Save updated config with missing defaults added
    if updated:
        with open(path, 'w') as f:
            json.dump(config, f, indent=4)
        print("Missing keys added to config.")

    return config, False

# Usage
config, first_start = load_config()
print(f"Config loaded successfully:")
for c in config:
    print(f"{c} = {config[c]}")

 # First start message
if first_start:
    print("Please fill in the IP addresses of both gloves and the corresponding COM-Ports you have created with com0com.")
    input("Press any key to exit")
else:
    start_server(config)
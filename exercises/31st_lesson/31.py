import logging
import os
import argparse
import json
from pathlib import Path
import sys

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

def validate_input():
    try:
        app_token = os.environ["APP_TOKEN"]
    except KeyError:
        logging.error("Missing environment variable APP_TOKEN.\nSet it with the following syntax:\nexport APP_TOKEN='<your_token_value>'")
        sys.exit(1)
    if not app_token.startswith(tuple(prefixes)):
        logging.error(f"The token is in the wrong format. It must start with one of the following prefixes:\n- {"\n- ".join(prefixes)}")
        sys.exit(2)

    APP_TOKEN = os.environ["APP_TOKEN"]
    APP_ORG = os.getenv("APP_ORG", "default_org")
    APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO")

    processed_vars = {
        "token_preview": APP_TOKEN[:4],
        "org": APP_ORG,
        "log_level": APP_LOG_LEVEL,
        "variables_loaded": 3
    }

    return ((APP_TOKEN, APP_ORG, APP_LOG_LEVEL, processed_vars))

parser = argparse.ArgumentParser(description="Loads three environment variables, shows a preview of APP_TOKEN, and shows the values of APP_ORG and APP_LOG_LEVEL.")
parser.add_argument("--output", action="store_true", help="Path to output file.")
args = parser.parse_args()

prefixes = {"tok_", "key_"}

processed_vars = validate_input()[3]

print(processed_vars)


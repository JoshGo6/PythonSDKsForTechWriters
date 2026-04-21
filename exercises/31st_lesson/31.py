import logging
import os
import argparse
import json
from pathlib import Path
import sys

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

parser = argparse.ArgumentParser(description="Loads three environment variables, shows a preview of APP_TOKEN, and shows the values of APP_ORG and APP_LOG_LEVEL.")
parser.add_argument("--output", action="store_true", help="Path to output file.")
args = parser.parse_args()

def validatation():
    try:
        app_token = os.environ["APP_TOKEN"]
    except KeyError:
        logging.error("Missing environment variable APP_TOKEN.")

validatation()

prefixes = {"tok_", "key_"}


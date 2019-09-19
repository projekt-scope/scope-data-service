"""
This script runs the server
"""
import os, sys

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(PROJECT_PATH, "src")
sys.path.append(SRC_PATH)
from app import app
from argparse import ArgumentParser


parser = ArgumentParser(description="Render - Microservice")
parser.add_argument(
    "-p",
    "--port",
    dest="port",
    required=False,
    help="input a valid port",
    metavar="PORT",
)
args = parser.parse_args()
port = args.port


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=args.port, threaded=True)

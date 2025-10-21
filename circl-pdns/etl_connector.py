#!/usr/bin/env python3
"""
CIRCL Passive DNS ETL connector (simple request + mock mode)
Author: Roshini Ragupathy
Roll No: 3122225001113

Instructions:
 - Copy example_config.env.sample -> .env and edit credentials
 - Set MOCK_MODE=true to test locally if you have no CIRCL creds
 - Run: python etl_connector.py --query example.com --max 10
"""

import os
import sys
import time
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Load .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "example_config.env.sample") if not os.path.exists(".env") else ".env")
# If user copied to .env, load that:
if os.path.exists(".env"):
    load_dotenv(".env")

CIRCL_USER = os.getenv("CIRCL_USERNAME")
CIRCL_PASS = os.getenv("CIRCL_PASSWORD")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "kyureeus_assignment")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "circl_passivedns_raw")
MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() in ("1", "true", "yes")

try:
    from pymongo import MongoClient, errors as pymongo_errors
except Exception as e:
    logger.error("pymongo not available; install requirements. Error: %s", e)
    raise

import requests
from requests.auth import HTTPBasicAuth

def get_mongo_collection(uri, db_name, coll_name):
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except Exception as e:
        logger.error("Cannot connect to MongoDB: %s", e)
        raise
    return client[db_name][coll_name]

def transform_record(record):
    doc = {}
    if isinstance(record, dict):
        doc.update(record)
    else:
        doc["value"] = str(record)
    doc["_ingested_at"] = datetime.utcnow()
    return doc

def extract_mock(query, rrtype=None):
    logger.warning("MOCK_MODE active. Returning demo records for: %s", query)
    return [
        {"rrname": query, "rrtype": "A", "rdata": "1.2.3.4", "first_seen": "2024-01-01T00:00:00Z"},
        {"rrname": "sub."+query, "rrtype": "A", "rdata": "5.6.7.8", "first_seen": "2024-02-01T00:00:00Z"},
    ]

def extract_with_requests(query, base_url="https://passive-dns.circl.lu", rrtype=None, max_results=None):
    logger.info("Querying CIRCL Passive DNS via HTTP: %s", query)
    endpoint = f"{base_url}/pdns/query/{query}"
    params = {}
    if rrtype:
        params["rrtype"] = rrtype
    auth = None
    if CIRCL_USER and CIRCL_PASS:
        auth = HTTPBasicAuth(CIRCL_USER, CIRCL_PASS)
    resp = requests.get(endpoint, params=params, auth=auth, timeout=30)
    if resp.status_code == 401:
        raise RuntimeError("Unauthorized: check CIRCL credentials.")
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict) and "results" in data:
        return data["results"][:max_results] if max_results else data["results"]
    if isinstance(data, list):
        return data[:max_results] if max_results else data
    return []

def run_etl(query, rrtype=None, max_extract=None):
    if MOCK_MODE:
        raw = extract_mock(query, rrtype)
    else:
        raw = extract_with_requests(query, rrtype=rrtype, max_results=max_extract)

    if not raw:
        logger.info("No records extracted for %s", query)
        return

    coll = get_mongo_collection(MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION)
    docs = [transform_record(r) for r in raw]
    try:
        res = coll.insert_many(docs)
        logger.info("Inserted %d documents into %s.%s", len(res.inserted_ids), MONGODB_DB, MONGODB_COLLECTION)
    except Exception as e:
        logger.error("Insert failed: %s", e)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="domain or IP to query (e.g., example.com)")
    parser.add_argument("--rrtype", default=None)
    parser.add_argument("--max", type=int, default=None)
    args = parser.parse_args()
    try:
        run_etl(args.query, args.rrtype, args.max)
    except Exception as e:
        logger.exception("ETL failed: %s", e)
        sys.exit(1)

# CIRCL Passive DNS ETL Connector
Author: Roshini Ragupathy
Roll No: 3122225001113

## Overview
Simple ETL connector to fetch Passive DNS data (CIRCL) and store into MongoDB.
Supports MOCK_MODE for local testing without CIRCL credentials.

## Files
- etl_connector.py — main script
- requirements.txt — dependencies
- example_config.env.sample — copy to .env and fill
- .gitignore — ignores .env

## Setup
1. Create Python venv:
   python -m venv venv
   .\venv\Scripts\Activate

2. Install:
   pip install -r requirements.txt

3. Copy sample .env:
   copy .\example_config.env.sample .env
   Edit .env; set MOCK_MODE=true to test without CIRCL creds.

## Run
python etl_connector.py --query example.com --max 10

## Notes
- Do NOT commit your .env file.
- If you have access to CIRCL credentials, set MOCK_MODE=false and fill CIRCL_USERNAME and CIRCL_PASSWORD in .env.

# Cash Flow Analyzer

A Dockerized Python script that generates fake transactions and analyzes them.

## Run locally
pip install -r requirements.txt
python cash_flow_analyzer.py

## Run with Docker
docker build -t cash-flow-analyzer .
docker run cash-flow-analyzer
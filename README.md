# Cash Flow Analyzer

A containerized data pipeline that generates fake financial transactions, analyzes cash flow, and ships the results to AWS S3 — built to learn the full dev-to-cloud workflow.

## Pipeline
Python Script → Docker → AWS ECR → ECS Fargate → S3
↓
CloudWatch

## What it does
- Generates 100 realistic fake bank transactions using Faker
- Calculates total income, expenses, net cash flow, and category breakdown
- Saves results to CSV and uploads to AWS S3 automatically
- Runs fully containerized on AWS ECS Fargate — no server management

## Tech stack
| Layer | Tool |
|-------|------|
| Language | Python 3.12 |
| Fake data | Faker |
| AWS SDK | boto3 |
| Container | Docker |
| Registry | AWS ECR |
| Compute | AWS ECS Fargate |
| Storage | AWS S3 |
| Logs | AWS CloudWatch |

## Run locally
```bash
pip install -r requirements.txt
python cash_flow_analyzer.py
```

## Run with Docker
```bash
docker build -t cash-flow-analyzer .
docker run -e AWS_ACCESS_KEY_ID=xxx \
           -e AWS_SECRET_ACCESS_KEY=xxx \
           -e AWS_BUCKET_NAME=your-bucket \
           -e AWS_REGION=eu-north-1 \
           cash-flow-analyzer
```

## Environment variables
| Variable | Description |
|----------|-------------|
| AWS_ACCESS_KEY_ID | IAM user access key |
| AWS_SECRET_ACCESS_KEY | IAM user secret key |
| AWS_BUCKET_NAME | Target S3 bucket name |
| AWS_REGION | AWS region |
# 🚀 Cloud Data Pipeline on AWS (Cash Flow Analyzer)

A production-style, containerized data pipeline that automates data processing and cloud deployment on AWS using Docker and CI/CD workflows.

---

## ⚙️ Tech Stack
Python • Docker • AWS (ECR, ECS Fargate, S3, CloudWatch) • GitHub Actions

---

## 🔧 What it does
- Generates financial transaction data  
- Calculates income, expenses, and net cash flow  
- Uploads results to AWS S3  
- Runs as a container on ECS Fargate  

---

## 🏗️ Architecture
Python → Docker → ECR → ECS Fargate → S3  
↓  
CloudWatch Logs  

---

## ▶️ Run Locally
```bash
pip install -r requirements.txt
python cash_flow_analyzer.py

## ▶️ Run With Docker
docker build -t cash-flow-analyzer .

docker run -e AWS_ACCESS_KEY_ID=xxx \
           -e AWS_SECRET_ACCESS_KEY=xxx \
           -e AWS_BUCKET_NAME=your-bucket \
           -e AWS_REGION=eu-north-1 \
           cash-flow-analyzer

import csv
import os
import json
import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

# ── Secrets Manager ───────────────────────────
def get_secrets() -> dict:
    secret_name = "cash-flow-analyzer/secrets"
    region = os.getenv("AWS_REGION", "eu-north-1")
    client = boto3.client(
        "secretsmanager",
        region_name=region,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

# ── Configuration ─────────────────────────────
secrets = get_secrets()
API_KEY = secrets["EXCHANGE_API_KEY"]
BASE_CURRENCY = "USD"
TRACKED_CURRENCIES = ["EUR", "GBP", "INR", "JPY", "AUD", "CAD", "CHF", "SGD"]

# ── Step 1: Fetch live exchange rates ─────────
def fetch_rates(base: str) -> dict:
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    print(f"  ✔ Fetched rates for {base} — last updated: {data['time_last_update_utc']}")
    return data

# ── Step 2: Analyze the rates ─────────────────
def analyze(data: dict) -> list[dict]:
    rates = data["conversion_rates"]
    base = data["base_code"]
    timestamp = data["time_last_update_utc"]

    results = []
    for currency in TRACKED_CURRENCIES:
        rate = rates.get(currency)
        if rate:
            results.append({
                "timestamp": timestamp,
                "base_currency": base,
                "target_currency": currency,
                "exchange_rate": rate,
                "1000_usd_equivalent": round(1000 * rate, 2),
            })
    return results

# ── Step 3: Save to CSV ───────────────────────
def save_to_csv(results: list[dict], filename: str = "exchange_rates.csv") -> None:
    fieldnames = ["timestamp", "base_currency", "target_currency", "exchange_rate", "1000_usd_equivalent"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"  ✔ Saved {len(results)} rates → {filename}")

# ── Step 4: Upload to S3 ──────────────────────
def upload_to_s3(filename: str) -> None:
    bucket = os.getenv("AWS_BUCKET_NAME")
    region = os.getenv("AWS_REGION")
    client = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    client.upload_file(filename, bucket, filename)
    print(f"  ✔ Uploaded {filename} → s3://{bucket}/{filename}")

# ── Step 5: Print report ──────────────────────
def print_report(results: list[dict]) -> None:
    bar = "─" * 42
    print(f"\n  💱  LIVE EXCHANGE RATE REPORT — {results[0]['base_currency']}")
    print(f"  {bar}")
    print(f"  {'Currency':<10} {'Rate':>12} {'1000 USD =':>15}")
    print(f"  {'─'*10} {'─'*12} {'─'*15}")
    for r in results:
        print(f"  {r['target_currency']:<10} {r['exchange_rate']:>12.4f} {r['1000_usd_equivalent']:>14.2f}")
    print()

# ── Main ──────────────────────────────────────
if __name__ == "__main__":
    print("\n⚙  Fetching live exchange rates...")
    data = fetch_rates(BASE_CURRENCY)

    print("⚙  Analyzing rates...")
    results = analyze(data)

    print("⚙  Saving CSV...")
    save_to_csv(results)

    print("⚙  Uploading to S3...")
    upload_to_s3("exchange_rates.csv")

    print_report(results)
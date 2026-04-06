import os
import boto3
from dotenv import load_dotenv
import csv
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────
NUM_TRANSACTIONS = 150
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)

CATEGORIES = {
    "income": ["Salary", "Freelance", "Investment", "Bonus", "Refund"],
    "expense": ["Rent", "Groceries", "Utilities", "Transport",
                "Entertainment", "Healthcare", "Dining", "Shopping"],
}

# ──────────────────────────────────────────────
# STEP 1 — Generate fake transactions
# ──────────────────────────────────────────────
def generate_transactions(n: int) -> list[dict]:
    transactions = []
    for _ in range(n):
        txn_type = random.choices(["income", "expense"], weights=[30, 70])[0]
        category = random.choice(CATEGORIES[txn_type])

        if txn_type == "income":
            amount = round(random.uniform(500, 8000), 2)
        else:
            amount = round(random.uniform(10, 1500), 2)

        date = fake.date_time_between(start_date=START_DATE, end_date=END_DATE)

        transactions.append({
            "date": date.strftime("%Y-%m-%d"),
            "description": fake.company() if txn_type == "income" else fake.bs().title(),
            "category": category,
            "type": txn_type,
            "amount": amount,
        })

    # Sort by date ascending
    transactions.sort(key=lambda x: x["date"])
    return transactions


# ──────────────────────────────────────────────
# STEP 2 — Analyze the transactions
# ──────────────────────────────────────────────
def analyze(transactions: list[dict]) -> dict:
    total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
    net_cash_flow = total_income - total_expense

    # Spending breakdown by category
    category_totals: dict[str, float] = {}
    for t in transactions:
        category_totals[t["category"]] = round(
            category_totals.get(t["category"], 0) + t["amount"], 2
        )

    top_expense_category = max(
        (k for k in category_totals if k in CATEGORIES["expense"]),
        key=lambda k: category_totals[k],
    )

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "net_cash_flow": round(net_cash_flow, 2),
        "category_totals": category_totals,
        "top_expense_category": top_expense_category,
        "num_transactions": len(transactions),
    }


# ──────────────────────────────────────────────
# STEP 3 — Save to CSV
# ──────────────────────────────────────────────
def save_to_csv(transactions: list[dict], filename: str = "transactions.csv") -> None:
    fieldnames = ["date", "description", "category", "type", "amount"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)
    print(f"  ✔ Saved {len(transactions)} transactions → {filename}")


# ──────────────────────────────────────────────
# STEP 4 — Print summary report
# ──────────────────────────────────────────────
def print_report(stats: dict) -> None:
    bar = "─" * 42
    print(f"\n{'':>4}💰  CASH FLOW SUMMARY REPORT")
    print(f"  {bar}")
    print(f"  Transactions analysed : {stats['num_transactions']}")
    print(f"  Total Income          : ${stats['total_income']:>10,.2f}")
    print(f"  Total Expenses        : ${stats['total_expense']:>10,.2f}")
    print(f"  {bar}")
    net = stats['net_cash_flow']
    sign = "+" if net >= 0 else ""
    print(f"  Net Cash Flow         : {sign}${net:>10,.2f}  {'✅' if net >= 0 else '⚠️ '}")
    print(f"  {bar}")
    print(f"  Top Expense Category  : {stats['top_expense_category']}")
    print(f"\n  {'Category':<20} {'Total':>10}")
    print(f"  {'─'*20} {'─'*10}")
    for cat, total in sorted(stats["category_totals"].items(),
                              key=lambda x: -x[1]):
        print(f"  {cat:<20} ${total:>9,.2f}")
    print()


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def upload_to_s3(filename: str) -> None:
    load_dotenv()
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

if __name__ == "__main__":
    print("\n⚙  Generating transactions...")
    txns = generate_transactions(NUM_TRANSACTIONS)

    print("⚙  Analysing data...")
    stats = analyze(txns)

    print("⚙  Saving CSV...")
    save_to_csv(txns)

    print("⚙  Uploading to S3...")
    upload_to_s3("transactions.csv")

    print_report(stats)

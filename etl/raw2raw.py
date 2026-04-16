import json
from datetime import datetime, timezone
from pyspark.sql.functions import lit

ingested_at = datetime.now(timezone.utc).isoformat()

all_accounts = []
all_transactions = []

for item_id in ITEMS_ID:
    accounts_response = list_accounts(item_id)
    if accounts_response is None:
        print(f"Skipping item_id {item_id}: failed to fetch accounts")
        continue

    accounts = accounts_response.get("results", [])
    all_accounts.extend(accounts)

    for account in accounts:
        account_id = account.get("id")
        transactions_response = list_transactions(account_id)
        if transactions_response is None:
            print(f"Skipping account {account_id}: failed to fetch transactions")
            continue
        transactions = transactions_response.get("results", [])
        for txn in transactions:
            txn["accountId"] = account_id
        all_transactions.extend(transactions)

if all_accounts:
    accounts_df = spark.read.json(
        spark.sparkContext.parallelize([json.dumps(a) for a in all_accounts])
    )
    accounts_df = accounts_df.withColumn("_ingested_at", lit(ingested_at))
    write_delta(accounts_df, "data/raw/accounts")
    print(f"raw/accounts: {accounts_df.count()} rows written")
else:
    print("No accounts fetched — raw/accounts not written")

if all_transactions:
    transactions_df = spark.read.json(
        spark.sparkContext.parallelize([json.dumps(t) for t in all_transactions])
    )
    transactions_df = transactions_df.withColumn("_ingested_at", lit(ingested_at))
    write_delta(transactions_df, "data/raw/transactions")
    print(f"raw/transactions: {transactions_df.count()} rows written")
else:
    print("No transactions fetched — raw/transactions not written")

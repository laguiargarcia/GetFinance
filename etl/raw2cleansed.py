import re
from pyspark.sql.functions import col, current_timestamp
from pyspark.sql.types import DoubleType, DateType


def camel_to_snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


# --- Cleanse accounts ---
accounts_raw = read_delta("data/raw/accounts")
accounts_cleansed = accounts_raw.withColumn("balance", col("balance").cast(DoubleType()))
accounts_cleansed = accounts_cleansed.select(
    [col(c).alias(camel_to_snake(c)) for c in accounts_cleansed.columns]
)
accounts_cleansed = accounts_cleansed.withColumn("processed_at", current_timestamp())
write_delta(accounts_cleansed, "data/cleansed/accounts")
print(f"cleansed/accounts: {accounts_cleansed.count()} rows written")
accounts_cleansed.printSchema()

# --- Cleanse transactions ---
transactions_raw = read_delta("data/raw/transactions")
transactions_cleansed = transactions_raw.withColumn("amount", col("amount").cast(DoubleType()))
transactions_cleansed = transactions_cleansed.withColumn("date", col("date").cast(DateType()))
transactions_cleansed = transactions_cleansed.select(
    [col(c).alias(camel_to_snake(c)) for c in transactions_cleansed.columns]
)
transactions_cleansed = transactions_cleansed.withColumn("processed_at", current_timestamp())
write_delta(transactions_cleansed, "data/cleansed/transactions")
print(f"cleansed/transactions: {transactions_cleansed.count()} rows written")
transactions_cleansed.printSchema()

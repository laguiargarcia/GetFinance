import pytest
import re
from pyspark.sql import Row
from pyspark.sql.functions import col, current_timestamp
from pyspark.sql.types import DoubleType, DateType


def camel_to_snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def test_camel_to_snake():
    assert camel_to_snake("currencyCode") == "currency_code"
    assert camel_to_snake("itemId") == "item_id"
    assert camel_to_snake("balance") == "balance"
    assert camel_to_snake("descriptionRaw") == "description_raw"


def test_accounts_balance_cast(spark, tmp_path_str):
    raw_path = tmp_path_str + "/raw/accounts"
    cleansed_path = tmp_path_str + "/cleansed/accounts"

    raw_data = [Row(id="1", name="Conta", balance="1500.50", currencyCode="BRL", itemId="item1")]
    raw_df = spark.createDataFrame(raw_data)
    raw_df.write.format("delta").mode("overwrite").save(raw_path)

    df = spark.read.format("delta").load(raw_path)
    df = df.withColumn("balance", col("balance").cast(DoubleType()))
    df = df.select([col(c).alias(camel_to_snake(c)) for c in df.columns])
    df.write.format("delta").mode("overwrite").save(cleansed_path)

    result = spark.read.format("delta").load(cleansed_path)
    row = result.collect()[0]
    assert row["balance"] == 1500.50
    assert "currency_code" in result.columns
    assert "item_id" in result.columns


def test_transactions_amount_and_date_cast(spark, tmp_path_str):
    raw_path = tmp_path_str + "/raw/transactions"
    cleansed_path = tmp_path_str + "/cleansed/transactions"

    raw_data = [Row(id="t1", description="Mercado", amount="-89.90", date="2024-03-15", accountId="acc1")]
    raw_df = spark.createDataFrame(raw_data)
    raw_df.write.format("delta").mode("overwrite").save(raw_path)

    df = spark.read.format("delta").load(raw_path)
    df = df.withColumn("amount", col("amount").cast(DoubleType()))
    df = df.withColumn("date", col("date").cast(DateType()))
    df = df.select([col(c).alias(camel_to_snake(c)) for c in df.columns])
    df.write.format("delta").mode("overwrite").save(cleansed_path)

    result = spark.read.format("delta").load(cleansed_path)
    row = result.collect()[0]
    assert row["amount"] == -89.90
    assert str(row["date"]) == "2024-03-15"
    assert "account_id" in result.columns

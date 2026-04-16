import pytest
from pyspark.sql import Row


def test_write_and_read_delta(spark, tmp_path_str):
    from storage import write_delta, read_delta
    path = tmp_path_str + "/test_table"
    data = [Row(id="1", name="conta corrente", balance=100.0)]
    df = spark.createDataFrame(data)

    write_delta(df, path)
    result = read_delta(path)

    assert result.count() == 1
    assert result.collect()[0]["id"] == "1"


def test_write_delta_overwrite(spark, tmp_path_str):
    from storage import write_delta, read_delta
    path = tmp_path_str + "/test_overwrite"
    df1 = spark.createDataFrame([Row(id="1")])
    df2 = spark.createDataFrame([Row(id="2")])

    write_delta(df1, path)
    write_delta(df2, path, mode="overwrite")
    result = read_delta(path)

    assert result.count() == 1
    assert result.collect()[0]["id"] == "2"

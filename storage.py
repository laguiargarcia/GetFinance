def write_delta(df, path, mode="overwrite"):
    df.write.format("delta").mode(mode).save(path)


def read_delta(path):
    from pyspark.sql import SparkSession
    spark = SparkSession.getActiveSession()
    if spark is None:
        raise RuntimeError("No active SparkSession found. Call write_delta or create a SparkSession before reading.")
    return spark.read.format("delta").load(path)

def write_delta(df, path, mode="overwrite"):
    df.write.format("delta").mode(mode).save(path)


def read_delta(path):
    from pyspark.sql import SparkSession
    spark = SparkSession.getActiveSession()
    return spark.read.format("delta").load(path)

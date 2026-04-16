with open("functions.py", "r", encoding="utf-8") as f:
    functions_code = f.read()
with open("dataBase.py", "r", encoding="utf-8") as g:
    dataBase_code = g.read()

exec(functions_code)
exec(dataBase_code)

result = list_accounts(ITEMS_ID[0])


spark = SparkSession.builder.appName("meuApp").getOrCreate()

df = spark.read.option("multiline", "true").json("dados.json")

df.show()
df.printSchema()
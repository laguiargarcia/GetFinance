import duckdb

con = duckdb.connect("getfinance.duckdb")
con.execute("INSTALL delta; LOAD delta;")
con.execute("""
    CREATE OR REPLACE VIEW transactions AS
    SELECT * FROM delta_scan('/app/data/cleansed/transactions')
""")
con.execute("""
    CREATE OR REPLACE VIEW accounts AS
    SELECT * FROM delta_scan('/app/data/cleansed/accounts')
""")
con.close()
print("getfinance.duckdb initialized with views")

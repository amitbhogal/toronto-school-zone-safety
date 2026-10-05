import duckdb

sql_file = "sql/profile_locations.sql"

with open(sql_file, "r") as file:
    sql = file.read()

result = duckdb.sql(sql)

print(result)
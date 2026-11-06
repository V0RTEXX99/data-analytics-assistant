
import pandas as pd

from database import (
    load_dataframe_into_database,
    execute_sql
)

print("Starting PostgreSQL test...")

# 1. Create sample dataset
df = pd.DataFrame({
    "city": ["Mumbai", "Delhi", "Mumbai", "Pune", "Delhi", "Pune"],
    "revenue": [24000, 19000, 6000, 14000, 3000, 2000]
})

# 2. Upload dataset to PostgreSQL
load_dataframe_into_database(df, "test_data")

print("\nSUCCESS: Data uploaded to PostgreSQL!")

# 3. Retrieve uploaded data
result = execute_sql("SELECT * FROM test_data")

print("\nUploaded records:")
print(result)

# 4. Test SQL aggregation
summary = execute_sql("""
    SELECT city, SUM(revenue) AS total_revenue
    FROM test_data
    GROUP BY city
    ORDER BY total_revenue DESC
""")

print("\nRevenue summary:")
print(summary)

print("\nALL POSTGRESQL TESTS PASSED!")

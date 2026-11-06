
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text

load_dotenv()

required = [
    "DB_HOST",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD"
]

missing = [key for key in required if not os.getenv(key)]

if missing:
    raise ValueError(f"Missing environment variables: {missing}")

url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME")
)

engine = create_engine(url)

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        )

        database, user = result.fetchone()

        print("POSTGRESQL CONNECTION SUCCESSFUL!")
        print("Database:", database)
        print("User:", user)

except Exception as error:
    print("CONNECTION FAILED:", error)

finally:
    engine.dispose()

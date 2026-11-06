import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
member_2_path = os.path.dirname(current_dir)
sys.path.insert(0, member_2_path)

from main.sql_generator import generate_sql

schema = {
    "table_name": "zomato_delivery",
    "columns": {
        "id": "VARCHAR",
        "delivery_person_id": "VARCHAR",
        "delivery_person_age": "INTEGER",
        "delivery_person_ratings": "NUMERIC",
        "restaurant_latitude": "NUMERIC",
        "restaurant_longitude": "NUMERIC",
        "delivery_location_latitude": "NUMERIC",
        "delivery_location_longitude": "NUMERIC",
        "order_date": "DATE",
        "time_ordered": "TEXT",
        "time_order_picked": "TEXT",
        "weatherconditions": "TEXT",
        "road_traffic_density": "TEXT",
        "vehicle_condition": "INTEGER",
        "type_of_order": "TEXT",
        "type_of_vehicle": "TEXT",
        "multiple_deliveries": "INTEGER",
        "festival": "TEXT",
        "city": "TEXT",
        "time_taken_min": "INTEGER",
    },
}

question = "Sort cities by average delivery ratings from highest to lowest"

result = generate_sql(schema, question)


print("\n" + "=" * 70)
print("USER QUESTION:")
print(question)

print("\nSTATUS:")
print(result["status"])

print("\nPRIMARY SQL:")
print(result.get("primary_sql"))

print("\nALTERNATIVE SQL:")
print(result.get("alternative_sql"))

print("\nERROR:")
print(result.get("error"))

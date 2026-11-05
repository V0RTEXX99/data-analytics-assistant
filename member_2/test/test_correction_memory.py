from ai.correction_memory import load_corrections, save_correction
import json

corrections = load_corrections()

# Remove exact duplicate entries
unique_corrections = []

for correction in corrections:
    if correction not in unique_corrections:
        unique_corrections.append(correction)

# Save cleaned memory
with open("correction_memory.json", "w", encoding="utf-8") as file:
    json.dump(unique_corrections, file, indent=4)

print("Duplicate corrections removed!")
print("Total corrections:", len(unique_corrections))

before = len(load_corrections())

save_correction(
    original_sql="SELEC city FROM zomato;",
    corrected_sql="SELECT city FROM zomato;",
    error_message="Invalid SQL syntax",
)

after = len(load_corrections())

print("Corrections before:", before)
print("Corrections after:", after)

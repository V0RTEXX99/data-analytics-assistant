
import pandas as pd
from ai_insights import generate_ai_insights

df = pd.DataFrame({
    "city": ["Mumbai", "Delhi", "Pune"],
    "total_revenue": [30000, 22000, 16000]
})

print("Generating AI insights...")

insights = generate_ai_insights(
    df,
    question="Which city performed best and what should the business do?"
)

print("\nAI INSIGHTS:")
print(insights)

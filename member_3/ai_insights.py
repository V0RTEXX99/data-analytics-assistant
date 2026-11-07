import os
import pandas as pd

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def prepare_dataset_summary(df):
    """Calculate reliable and compact dataset statistics."""

    summary = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "missing_values": {},
        "numeric_analysis": {},
        "categorical_analysis": {},
        "datetime_analysis": {}
    }

    for column in df.columns:

        missing_count = int(df[column].isnull().sum())

        if missing_count > 0:
            summary["missing_values"][column] = missing_count

        if pd.api.types.is_numeric_dtype(df[column]):

            numeric_data = df[column].dropna()

            if not numeric_data.empty:
                summary["numeric_analysis"][column] = {
                    "total": float(numeric_data.sum()),
                    "average": float(numeric_data.mean()),
                    "median": float(numeric_data.median()),
                    "minimum": float(numeric_data.min()),
                    "maximum": float(numeric_data.max())
                }

        elif pd.api.types.is_datetime64_any_dtype(df[column]):

            dates = df[column].dropna()

            if not dates.empty:
                summary["datetime_analysis"][column] = {
                    "earliest": str(dates.min()),
                    "latest": str(dates.max())
                }

        else:

            counts = df[column].value_counts(dropna=True)

            summary["categorical_analysis"][column] = {
                "unique_values": int(df[column].nunique()),
                "most_frequent": counts.head(5).to_dict(),
                "least_frequent": counts.tail(5).to_dict()
            }

    return summary


def generate_ai_insights(df, question=None):
    """
    Generate AI-powered business insights
    from uploaded datasets or SQL query results.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a Pandas DataFrame.")

    if df.empty:
        return "No data available to analyze."

    api_key = os.getenv("GROQ_API_KEY")
    model_name = os.getenv("GROQ_MODEL")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing from your .env file."
        )

    if not model_name:
        raise ValueError(
            "GROQ_MODEL is missing from your .env file."
        )

    dataset_summary = prepare_dataset_summary(df)

    # Limit sample size to control prompt length
    data_sample = df.head(10).to_string(index=False)

    prompt = f"""
You are an experienced business data analyst.

DATASET STATISTICS:
{dataset_summary}

SAMPLE DATA (first 10 rows):
{data_sample}

USER QUESTION:
{question if question else "Provide a general business analysis."}

Prepare the analysis using these sections:

1. KEY FINDINGS
- Identify important results.
- Mention actual highest and lowest values where relevant.

2. TRENDS AND PATTERNS
- Identify patterns supported by the dataset.
- Discuss time-based trends only when valid date information exists.

3. UNUSUAL OBSERVATIONS
- Identify unusual values only when supported by evidence.
- Mention missing values and data-quality concerns.

4. BUSINESS RECOMMENDATIONS
- Suggest practical actions.
- Explain why each recommendation is relevant.

5. SIMPLE SUMMARY
- Explain the overall situation in beginner-friendly language.

IMPORTANT RULES:
- Use calculated statistics as the source of truth.
- Never invent numbers or observations.
- Distinguish totals, averages, and individual values.
- Do not assume a high value is automatically good.
- Do not claim trends from insufficient data.
- Clearly mention limitations.
"""

    try:

        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an experienced business data analyst. "
                        "Provide accurate, evidence-based insights. "
                        "Never invent findings."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_completion_tokens=1500
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("The AI returned an empty response.")

        return content

    except Exception as e:
        raise RuntimeError(
            f"AI insight generation failed: {e}"
        ) from e

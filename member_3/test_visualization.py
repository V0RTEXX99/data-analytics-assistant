
import pandas as pd

from visualization import (
    analyze_result,
    get_chart_recommendations,
    create_chart
)


# TEST DATA: Includes duplicate cities
result_df = pd.DataFrame({
    "city": [
        "Mumbai", "Delhi", "Mumbai",
        "Pune", "Delhi", "Pune"
    ],
    "revenue": [
        24000, 19000, 6000,
        14000, 3000, 2000
    ]
})


print("\n========== DATA ANALYSIS ==========")

analysis = analyze_result(result_df)

print(analysis)


print("\n========== CHART RECOMMENDATIONS ==========")

recommendations = get_chart_recommendations(analysis)

print(recommendations)


# Expected aggregated revenue
expected = {
    "Mumbai": 30000,
    "Delhi": 22000,
    "Pune": 16000
}


print("\n========== BAR CHART TEST ==========")

bar_fig = create_chart(
    result_df,
    "Bar Chart",
    "city",
    "revenue"
)

bar_result = dict(
    zip(bar_fig.data[0].x, bar_fig.data[0].y)
)

assert bar_result == expected, "Bar chart calculation FAILED!"

print("Bar chart calculation PASSED!")
print(bar_result)


print("\n========== PIE CHART TEST ==========")

pie_fig = create_chart(
    result_df,
    "Pie Chart",
    "city",
    "revenue"
)

pie_result = dict(
    zip(pie_fig.data[0].labels, pie_fig.data[0].values)
)

assert pie_result == expected, "Pie chart calculation FAILED!"

print("Pie chart calculation PASSED!")
print(pie_result)


# Check total revenue
total_revenue = sum(bar_result.values())

assert total_revenue == 68000

print("\nTotal Revenue:", total_revenue)


# Check pie percentages
print("\nPie Chart Percentages:")

for city, revenue in pie_result.items():

    percentage = (revenue / total_revenue) * 100

    print(f"{city}: {percentage:.2f}%")


print("\n====================================")
print("ALL VISUALIZATION TESTS PASSED!")
print("====================================")

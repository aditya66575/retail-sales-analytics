import pandas as pd

df = pd.read_csv("data/raw/Supermarket Sales 2.csv")

print("First 5 rows:")
print(df.head())

print("\nDataset shape:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())
# ----- Data quality checks -----

# Convert Date from text to datetime
df["Date"] = pd.to_datetime(
    df["Date"],
    format="%m/%d/%Y",
    errors="coerce"
)

print("\nInvalid dates:", df["Date"].isna().sum())

print("\nDate range:")
print("Start:", df["Date"].min())
print("End:", df["Date"].max())

print("\nNumeric summary:")
print(df[["Unit price", "Quantity", "Rating"]].describe())

print("\nCheck non-positive prices:",
      (df["Unit price"] <= 0).sum())

print("Check non-positive quantities:",
      (df["Quantity"] <= 0).sum())

print("\nCategory values:")
for column in ["Branch", "Customer type", "Gender",
                "Product line", "Payment"]:
    print(f"\n{column}:")
    print(df[column].value_counts())
# ----- Sales Analysis -----

# Calculate sales amount for each record
df["Sales"] = df["Unit price"] * df["Quantity"]

# Overall business metrics
total_sales = df["Sales"].sum()
total_units = df["Quantity"].sum()
average_sale = df["Sales"].mean()

print("\n--- OVERALL SALES SUMMARY ---")
print(f"Total sales amount: {total_sales:,.2f}")
print(f"Total units sold: {total_units:,}")
print(f"Average sales per record: {average_sale:,.2f}")

# Sales by product line
product_sales = (
    df.groupby("Product line")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n--- SALES BY PRODUCT LINE ---")
print(product_sales.round(2))

# Sales by branch
branch_sales = (
    df.groupby("Branch")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n--- SALES BY BRANCH ---")
print(branch_sales.round(2))

# Sales by payment method
payment_sales = (
    df.groupby("Payment")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n--- SALES BY PAYMENT METHOD ---")
print(payment_sales.round(2))

import matplotlib.pyplot as plt
from pathlib import Path

# Create output folder
output_dir = Path("outputs/charts")
output_dir.mkdir(parents=True, exist_ok=True)


# Function to add labels above bars
def add_bar_labels(ax):
    for bar in ax.patches:
        height = bar.get_height()

        ax.annotate(
            f"{height:,.0f}",
            (bar.get_x() + bar.get_width() / 2, height),
            ha="center",
            va="bottom",
            fontsize=9,
            xytext=(0, 4),
            textcoords="offset points"
        )


# 1. Sales by Product Line
ax = product_sales.plot(
    kind="bar",
    figsize=(10, 5)
)

plt.title("Sales by Product Line")
plt.xlabel("Product Line")
plt.ylabel("Calculated Sales")
plt.xticks(rotation=35, ha="right")

add_bar_labels(ax)

plt.tight_layout()
plt.savefig(
    output_dir / "sales_by_product.png",
    dpi=200,
    bbox_inches="tight"
)
plt.close()


# 2. Sales by Branch
ax = branch_sales.plot(
    kind="bar",
    figsize=(8, 5)
)

plt.title("Sales by Branch")
plt.xlabel("Branch")
plt.ylabel("Calculated Sales")
plt.xticks(rotation=0)

add_bar_labels(ax)

plt.tight_layout()
plt.savefig(
    output_dir / "sales_by_branch.png",
    dpi=200,
    bbox_inches="tight"
)
plt.close()


# 3. Sales by Payment Method
ax = payment_sales.plot(
    kind="bar",
    figsize=(8, 5)
)

plt.title("Sales by Payment Method")
plt.xlabel("Payment Method")
plt.ylabel("Calculated Sales")
plt.xticks(rotation=0)

add_bar_labels(ax)

plt.tight_layout()
plt.savefig(
    output_dir / "sales_by_payment.png",
    dpi=200,
    bbox_inches="tight"
)
plt.close()


print("All charts saved successfully!")
print("Location:", output_dir.resolve())

# ----- Monthly Sales Analysis -----

# Group sales by month
df["Month"] = df["Date"].dt.to_period("M")

monthly_sales = (
    df.groupby("Month")["Sales"]
    .sum()
    .sort_index()
)

print("\n--- MONTHLY SALES ---")
print(monthly_sales.round(2))

print("\nHighest sales month:")
print(monthly_sales.idxmax(), round(monthly_sales.max(), 2))

print("\nLowest sales month:")
print(monthly_sales.idxmin(), round(monthly_sales.min(), 2))


# ----- Monthly Sales Trend Chart -----

monthly_sales.index = monthly_sales.index.astype(str)

ax = monthly_sales.plot(
    kind="line",
    marker="o",
    figsize=(10, 5)
)

plt.title("Monthly Sales Trend - 2024")
plt.xlabel("Month")
plt.ylabel("Calculated Sales")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    output_dir / "monthly_sales_trend.png",
    dpi=200,
    bbox_inches="tight"
)

plt.close()

print("\nMonthly sales chart saved successfully!")

print("\nMonthly transaction counts:")
print(df.groupby("Month").size())

print("\nMonthly units sold:")
print(df.groupby("Month")["Quantity"].sum())

# ----- Monthly Performance Comparison -----

monthly_report = df.groupby("Month").agg(
    Records=("Sales", "count"),
    Units_Sold=("Quantity", "sum"),
    Total_Sales=("Sales", "sum"),
    Average_Units_Per_Record=("Quantity", "mean"),
    Average_Sales_Per_Record=("Sales", "mean")
)

print("\n--- MONTHLY PERFORMANCE REPORT ---")
print(monthly_report.round(2).to_string())

print("\n--- APRIL vs MAY ---")
print(monthly_report.loc[["2024-04", "2024-05"]].round(2))

# ----- Investigate April-May Sales Drop -----

monthly_details = df.groupby("Month").agg(
    Total_Sales=("Sales", "sum"),
    Total_Units=("Quantity", "sum"),
    Records=("Sales", "count"),
    Average_Unit_Price=("Unit price", "mean"),
    Average_Quantity=("Quantity", "mean")
)

print("\n--- APRIL vs MAY COMPARISON ---")
print(
    monthly_details.loc[["2024-04", "2024-05"]]
    .round(2)
    .to_string()
)

print("\n--- SALES BY PRODUCT LINE: APRIL vs MAY ---")

product_month = df.groupby(
    ["Month", "Product line"]
)["Sales"].sum().unstack()

print(product_month.loc[["2024-04", "2024-05"]].round(2))

# ----- Product Line Investigation -----

product_month_report = df.groupby(
    ["Month", "Product line"]
).agg(
    Records=("Sales", "count"),
    Units_Sold=("Quantity", "sum"),
    Total_Sales=("Sales", "sum")
)

print("\n--- APRIL: PRODUCT LINE DETAILS ---")
print(
    product_month_report.loc["2024-04"]
    .round(2)
    .to_string()
)

print("\n--- MAY: PRODUCT LINE DETAILS ---")
print(
    product_month_report.loc["2024-05"]
    .round(2)
    .to_string()
)

# ----- Export Cleaned Dataset -----

from pathlib import Path

processed_dir = Path("data/processed")
processed_dir.mkdir(parents=True, exist_ok=True)

# Export data with the corrected Date column
df.to_csv(
    processed_dir / "supermarket_sales_cleaned.csv",
    index=False
)

print("\nCleaned dataset exported successfully!")
print(
    "File:",
    (processed_dir / "supermarket_sales_cleaned.csv").resolve()
)
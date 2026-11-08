import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Locate the Excel file beside this Python script
folder = Path(__file__).resolve().parent
excel_file = folder / "DAV - FUEL-1.xlsx"
output_folder = folder / "Fuel_Graphs"
output_folder.mkdir(exist_ok=True)

# Load dataset
df = pd.read_excel(excel_file, sheet_name="Sheet1")
df.columns = df.columns.astype(str).str.strip()

# Select and rename columns
df = df[[
    "District", "Year",
    "Petrol Price (INR/Litre)",
    "Diesel Price (INR/Litre)",
    "Petrol Consumption (KL)",
    "Diesel Consumption (KL)",
    "Total fuel consumption(KL)"
]].copy()

df.columns = [
    "District", "Year", "Petrol_Price", "Diesel_Price",
    "Petrol_Consumption", "Diesel_Consumption",
    "Total_Fuel_Consumption"
]

# Clean values
df["District"] = df["District"].astype("string").str.strip()

numeric_cols = df.columns.drop("District")
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=[
    "District", "Year", "Petrol_Consumption",
    "Diesel_Consumption", "Total_Fuel_Consumption"
])
df = df.drop_duplicates()

# Save cleaned data
df.to_excel(folder / "DAV_FUEL_CLEANED.xlsx", index=False)

# Calculate yearly totals
yearly = df.groupby("Year", as_index=False).agg({
    "Petrol_Consumption": "sum",
    "Diesel_Consumption": "sum",
    "Total_Fuel_Consumption": "sum"
})

# Calculate district totals
districts = df.groupby("District")[
    "Total_Fuel_Consumption"
].sum().sort_values(ascending=False)

sns.set_theme(style="whitegrid")

# Graph 1: Yearly trend
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(yearly["Year"], yearly["Total_Fuel_Consumption"], marker="o")
ax.set_title("Yearly Total Fuel Consumption")
ax.set_xlabel("Year")
ax.set_ylabel("Consumption (KL)")
fig.tight_layout()
fig.savefig(output_folder / "1_Yearly_Trend.png", dpi=200)
plt.close(fig)

# Graph 2: Petrol vs diesel
fig, ax = plt.subplots(figsize=(9, 5))
yearly.plot(
    x="Year",
    y=["Petrol_Consumption", "Diesel_Consumption"],
    kind="bar",
    ax=ax
)
ax.set_title("Petrol vs Diesel Consumption")
ax.set_ylabel("Consumption (KL)")
ax.tick_params(axis="x", rotation=0)
fig.tight_layout()
fig.savefig(output_folder / "2_Petrol_vs_Diesel.png", dpi=200)
plt.close(fig)

# Graph 3: Top 10 districts
fig, ax = plt.subplots(figsize=(9, 6))
districts.head(10).sort_values().plot(kind="barh", ax=ax)
ax.set_title("Top 10 Districts by Fuel Consumption")
ax.set_xlabel("Consumption (KL)")
fig.tight_layout()
fig.savefig(output_folder / "3_Top_10_Districts.png", dpi=200)
plt.close(fig)

# Graph 4: Bottom 10 districts
fig, ax = plt.subplots(figsize=(9, 6))
districts.tail(10).sort_values().plot(kind="barh", ax=ax)
ax.set_title("Bottom 10 Districts by Fuel Consumption")
ax.set_xlabel("Consumption (KL)")
fig.tight_layout()
fig.savefig(output_folder / "4_Bottom_10_Districts.png", dpi=200)
plt.close(fig)

# Graph 5: District heatmap
heatmap = df.pivot_table(
    index="District",
    columns="Year",
    values="Total_Fuel_Consumption",
    aggfunc="sum"
)
fig, ax = plt.subplots(figsize=(10, 12))
sns.heatmap(heatmap, cmap="YlOrRd", ax=ax)
ax.set_title("District-wise Fuel Consumption Heatmap")
fig.tight_layout()
fig.savefig(output_folder / "5_District_Heatmap.png", dpi=200)
plt.close(fig)

# Graph 6: Average fuel prices
prices = df.groupby("Year", as_index=False).agg({
    "Petrol_Price": "mean",
    "Diesel_Price": "mean"
})
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(prices["Year"], prices["Petrol_Price"], marker="o", label="Petrol")
ax.plot(prices["Year"], prices["Diesel_Price"], marker="o", label="Diesel")
ax.set_title("Average Petrol and Diesel Prices")
ax.set_xlabel("Year")
ax.set_ylabel("Price (INR/Litre)")
ax.legend()
fig.tight_layout()
fig.savefig(output_folder / "6_Fuel_Price_Comparison.png", dpi=200)
plt.close(fig)

# Report results
graphs = list(output_folder.glob("*.png"))
print("Analysis completed!")
print("Graphs created:", len(graphs))
print("Graph folder:", output_folder)

for graph in sorted(graphs):
    print(graph.name)
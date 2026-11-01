import matplotlib.pyplot as plt
import pandas as pd

def pause():
    input("\nPress Enter for the next step...")


online_rt = pd.read_csv("resources/visualization/Online_Retail.csv", encoding="latin1")

# ---------- Countries with the most orders ----------

# step 1
print("Create histogram of 10 countries with most Quantity except UK - [.plot(kind='bar')]")
not_uk = online_rt[online_rt["Country"] != "United Kingdom"]
not_uk.groupby("Country")["Quantity"].sum().nlargest(10).plot(kind="bar")
plt.show()
pause()

# step 2
print("Exclude negative Quantity entries - [online_rt[online_rt['Quantity'] > 0]]")
online_rt = online_rt[online_rt["Quantity"] > 0]
print(online_rt.shape[0])
pause()

# ---------- First attempt: Quantity per UnitPrice by CustomerID ----------

# step 3
print("Create scatterplot of Quantity per UnitPrice by CustomerID for top 3 countries - [.scatter()]")
top3 = online_rt[online_rt["Country"] != "United Kingdom"].groupby("Country")["Quantity"].sum().nlargest(3).index
customers = online_rt[online_rt["Country"].isin(top3)].groupby(["CustomerID", "Country"]).sum(numeric_only=True)

def scatter_by_country(data, x):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, country in zip(axes, top3):
        country_data = data.xs(country, level="Country")
        ax.scatter(country_data[x], country_data["Quantity"])
        ax.set_title(country)
        ax.set_xlabel(x)
        ax.set_ylabel("Quantity")
    plt.show()

scatter_by_country(customers, "UnitPrice")
pause()

# ---------- Why is the first attempt uninformative? ----------

# step 4
print("Display first rows of that DataFrame - [.head()]")
print(customers.head())
pause()

# step 5
print("Display dtype of UnitPrice - [.dtype]")
print(customers["UnitPrice"].dtype)
pause()

# step 6
print("Pull data for CustomerIDs 12346.0 and 12347.0 - [.isin()]")
print(online_rt[online_rt["CustomerID"].isin([12346.0, 12347.0])])
pause()

# ---------- Reinterpreting the problem: AvgPrice per customer ----------

# step 7
print("Find top 3 countries in terms of sales volume - [.nlargest(3)]")
print(top3)
pause()

# step 8
print("Add Revenue column - [Quantity * UnitPrice]")
online_rt["Revenue"] = online_rt["Quantity"] * online_rt["UnitPrice"]
print(online_rt.head())
pause()

# step 9
print("Group by CustomerID and Country and get AvgPrice - [.groupby().agg()]")
customers = online_rt[online_rt["Country"].isin(top3)].groupby(["CustomerID", "Country"]).agg(
    Quantity=("Quantity", "sum"), Revenue=("Revenue", "sum")
)
customers["AvgPrice"] = customers["Revenue"] / customers["Quantity"]
print(customers.head())
pause()

# step 10
print("Plot Quantity per AvgPrice for each country - [.scatter()]")
scatter_by_country(customers, "AvgPrice")
pause()

# ---------- All countries on a single graph ----------

# step 11
print("Plot all CustomerIDs on a single graph - [.scatter()]")
plt.scatter(customers["AvgPrice"], customers["Quantity"])
plt.show()
pause()

# step 12
print("Zoom in on the curve - [plt.xlim(), plt.ylim()]")
plt.scatter(customers["AvgPrice"], customers["Quantity"])
plt.xlim(0, 6)
plt.ylim(0, 10000)
plt.show()
pause()

# ---------- Revenue per UnitPrice ----------

# step 13
print("Group UnitPrice by intervals of 1 for [0, 50) and sum Quantity and Revenue - [.groupby(astype(int)).sum()]")
cheap = online_rt[online_rt["UnitPrice"].between(0, 50, inclusive="left")]
by_price = cheap.groupby(cheap["UnitPrice"].astype(int))[["Quantity", "Revenue"]].sum()
print(by_price)
pause()

# step 14
print("Plot line chart of revenue per UnitPrice - [.plot()]")
by_price["Revenue"].plot()
plt.show()
pause()

# step 15
print("Make the plot nicer - [.set_xticks(), revenue in millions]")
ax = (by_price["Revenue"] / 1e6).plot()
ax.set_xticks(range(0, 50, 5))
ax.set_xlabel("UnitPrice")
ax.set_ylabel("Revenue (millions)")
plt.show()
pause()

# ---------- Bonus ----------

# step 16
print("Which 5 products were ordered the most? - [.groupby('Description')['Quantity'].sum().nlargest(5)]")
print(online_rt.groupby("Description")["Quantity"].sum().nlargest(5))

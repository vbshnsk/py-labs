import pandas as pd

drinks = pd.read_csv("resources/grouping/drinks.csv", keep_default_na=False)

# step 1
print("Get continent that drinks more beer on average - [.groupby().mean().idxmax()]")
print(drinks.groupby("continent")["beer_servings"].mean().idxmax())

# step 2
print("Get wine consumption statistics per continent - [.groupby().describe()]")
print(drinks.groupby("continent")["wine_servings"].describe())

# step 3
print("Get mean alcohol consumption per continent for every column - [.groupby().mean()]")
print(drinks.groupby("continent").mean(numeric_only=True))

# step 4
print("Get median alcohol consumption per continent for every column - [.groupby().median()]")
print(drinks.groupby("continent").median(numeric_only=True))

# step 5
print("Get mean, min and max of spirit consumption as DataFrame - [.groupby().agg([...])]")
print(drinks.groupby("continent")["spirit_servings"].agg(["mean", "min", "max"]))

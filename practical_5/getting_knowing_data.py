import pandas as pd

food = pd.read_csv("resources/getting-knowing-data/openfoodfacts_lite.csv", index_col=0, low_memory=False)

# step 1
print("Get first 5 entries - [.head()]")
print(food.head())

# step 2
print("Get number of observations - [.shape[0]]")
print(food.shape[0])

# step 3
print("Get number of columns - [.shape[1]]")
print(food.shape[1])

# step 4
print("Get names of all columns - [.columns]")
print(list(food.columns))

# step 5
print("Get name of the 105th column - [.columns[104]]")
print(food.columns[104])

# step 6
print("Get type of the 105th column - [.iloc[:, 104].dtype]")
print(food.iloc[:, 104].dtype)

# step 7
print("Get how the dataset is indexed - [.index]")
print(food.index)

# step 8
print("Get product name of the 19th observation - [.iloc[18]['product_name']]")
print(food.iloc[18]["product_name"])

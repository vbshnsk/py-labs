import numpy as np
import pandas as pd

cars1 = pd.read_csv("resources/merge/cars1.csv")
cars2 = pd.read_csv("resources/merge/cars2.csv")

# step 1
print("Fix cars1 unnamed blank columns - [.dropna(axis=1, how='all')]")
cars1 = cars1.dropna(axis=1, how="all")
print(cars1.columns)

# step 2
print("Get number of observations in each dataset - [.shape[0]]")
print(cars1.shape[0])
print(cars2.shape[0])

# step 3
print("Join cars1 and cars2 into cars - [pd.concat()]")
cars = pd.concat([cars1, cars2], ignore_index=True)
print(cars)

# step 4
print("Create random owners Series from 15000 to 73000 - [np.random.randint()]")
owners = pd.Series(np.random.randint(15000, 73001, size=cars.shape[0]))
print(owners)

# step 5
print("Add column owners to cars - [cars['owners'] = ...]")
cars["owners"] = owners
print(cars.head())

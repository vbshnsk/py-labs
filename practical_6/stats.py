import pandas as pd

baby_names = pd.read_csv("resources/stats/US_Baby_Names_right.csv")

# step 1
print("See the first 10 entries - [.head(10)]")
print(baby_names.head(10))

# step 2
print("Delete columns 'Unnamed: 0' and 'Id' - [.drop(columns=[...])]")
baby_names = baby_names.drop(columns=["Unnamed: 0", "Id"])
print(baby_names.head())

# step 3
print("Get whether there are more male or female names - [.value_counts()]")
print(baby_names["Gender"].value_counts())

# step 4
print("Group by name and assign to names - [.groupby()['Count'].sum()]")
names = baby_names.groupby("Name")["Count"].sum()
print(names)

# step 5
print("Get number of different names - [.shape[0]]")
print(names.shape[0])

# step 6
print("Get name with most occurrences - [.idxmax()]")
print(names.idxmax())

# step 7
print("Get number of names with the least occurrences - [(names == names.min()).sum()]")
print((names == names.min()).sum())

# step 8
print("Get median name occurrence - [.median()]")
print(names.median())

# step 9
print("Get standard deviation of names - [.std()]")
print(names.std())

# step 10
print("Get summary of mean, min, max, std and quartiles - [.describe()]")
print(names.describe())

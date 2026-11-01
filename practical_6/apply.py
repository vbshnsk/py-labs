import pandas as pd

df = pd.read_csv("resources/apply/student-mat.csv")

# step 1
print("Slice from 'school' until 'guardian' column - [.loc[:, 'school':'guardian']]")
df = df.loc[:, "school":"guardian"]
print(df.head())

# step 2
print("Create lambda that capitalizes strings - [lambda x: x.capitalize()]")
capitalizer = lambda x: x.capitalize()
print(capitalizer("teacher"))

# step 3
print("Capitalize Mjob and Fjob - [.apply()]")
df["Mjob"].apply(capitalizer)
df["Fjob"].apply(capitalizer)

# step 4
print("Print last elements of the data set - [.tail()]")
print(df.tail())

# step 5
print("Original is still lowercase because apply returns a new Series, assign it back - [df[col] = ...]")
df["Mjob"] = df["Mjob"].apply(capitalizer)
df["Fjob"] = df["Fjob"].apply(capitalizer)
print(df.tail())

# step 6
print("Create majority function and legal_drinker column - [.apply(majority)]")
def majority(age):
    return age > 17

df["legal_drinker"] = df["age"].apply(majority)
print(df.head())

# step 7
print("Multiply every number of the dataset by 10 - [.map()]")
def times10(x):
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return x * 10
    return x

print(df.map(times10).head())

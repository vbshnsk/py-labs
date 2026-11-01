import pandas as pd

euro12 = pd.read_csv("resources/filtering-sorting/Euro_2012_stats_TEAM.csv")

# step 1
print("Select only the Goals column - [['Goals']]")
print(euro12["Goals"])

# step 2
print("Get number of teams - [.nunique()]")
print(euro12["Team"].nunique())

# step 3
print("Get number of columns - [.shape[1]]")
print(euro12.shape[1])

# step 4
print("View Team, Yellow Cards and Red Cards as discipline - [[[...]]]")
discipline = euro12[["Team", "Yellow Cards", "Red Cards"]]
print(discipline)

# step 5
print("Sort by Red Cards, then Yellow Cards - [.sort_values(by=[...])]")
print(discipline.sort_values(by=["Red Cards", "Yellow Cards"], ascending=False))

# step 6
print("Get mean Yellow Cards per team - [.mean()]")
print(discipline["Yellow Cards"].mean())

# step 7
print("Filter teams that scored more than 6 goals - [euro12[euro12['Goals'] > 6]]")
print(euro12[euro12["Goals"] > 6])

# step 8
print("Select teams that start with G - [.str.startswith('G')]")
print(euro12[euro12["Team"].str.startswith("G")])

# step 9
print("Select first 7 columns - [.iloc[:, :7]]")
print(euro12.iloc[:, :7])

# step 10
print("Select all columns except the last 3 - [.iloc[:, :-3]]")
print(euro12.iloc[:, :-3])

# step 11
print("Present Shooting Accuracy from England, Italy and Ukraine - [.loc[.isin([...]), ...]]")
print(euro12.loc[euro12["Team"].isin(["England", "Italy", "Ukraine"]), ["Team", "Shooting Accuracy"]])

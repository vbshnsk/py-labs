# Bonus: repeat the cold start (steps 5-8 of cold_start.py) for several different random users
import ast
import re
import time

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 50)
pd.set_option("display.max_columns", None)
pd.set_option("display.precision", 3)

ITERATIONS = 5
K = 10
M = 1000
LIKED = 4
TAG_HEADINGS = {"preparation", "time_to_make", "course", "main_ingredient", "dietary", "occasion", "cuisine",
                "low_in_something", "equipment", "number_of_servings", "technique", "taste_mood"}
COURSES = {"main_dish", "desserts", "side_dishes", "appetizers", "breakfast", "lunch", "brunch", "salads",
           "soups_stews", "breads", "beverages", "snacks", "condiments_etc"}
MAIN_INGREDIENTS = {"meat", "poultry", "seafood", "vegetables", "fruit", "eggs_dairy", "pasta_rice_and_grains", "chocolate"}


def pause():
    input("\nPress Enter for the next step...")


def normalize(token):
    return re.sub(r"[^a-z0-9]+", "_", token.lower()).strip("_")


def user_split(user_id):
    user_liked = liked[liked["user_id"] == user_id].sort_values("date")
    favourites = user_liked[user_liked["rating"] == 5]["recipe_id"].head(3).tolist()
    return favourites, set(user_liked["recipe_id"]) - set(favourites)


def recommend(matrix, favourites):
    fav_rows = recipes.index.get_indexer(favourites)
    profile = np.asarray(matrix[fav_rows].mean(axis=0))
    scores = cosine_similarity(profile, matrix).ravel()
    scores[fav_rows] = -1
    return recipes.index[np.argsort(-scores)[:K]]


def precision_at_k(rec_ids, relevant):
    return sum(r in relevant for r in rec_ids) / K


def ndcg_at_k(rec_ids, relevant):
    dcg = sum(1 / np.log2(i + 2) for i, r in enumerate(rec_ids) if r in relevant)
    idcg = sum(1 / np.log2(i + 2) for i in range(min(K, len(relevant))))
    return dcg / idcg


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b)


def coverage(rec_ids, group):
    return len(set(recipes.loc[rec_ids, "tags"].sum()) & group)


# ---------- Data (same preparation as cold_start.py steps 1-3) ----------

print("Load and prepare the data, build the soup (tags + ingredients) - [same as cold_start.py steps 1-3]")
recipes = pd.read_csv("resources/RAW_recipes.csv", usecols=["id", "name", "tags", "ingredients"]).dropna(subset=["name"])
interactions = pd.read_csv("resources/RAW_interactions.csv", usecols=["user_id", "recipe_id", "date", "rating"])
interactions = interactions[(interactions["rating"] > 0) & interactions["recipe_id"].isin(recipes["id"])]
for col in ["tags", "ingredients"]:
    recipes[col] = recipes[col].apply(lambda s: [normalize(t) for t in ast.literal_eval(s)])
recipes["soup"] = (recipes["tags"].apply(lambda tokens: [t for t in tokens if t not in TAG_HEADINGS])
                   + recipes["ingredients"]).str.join(" ")
recipes = recipes.set_index("id")
liked = interactions[interactions["rating"] >= LIKED]
liked_per_user = liked.groupby("user_id").size()
token_freq = recipes["soup"].str.split().explode().value_counts()
print(f"recipes {len(recipes)}, interactions {len(interactions)}")

print("\nBuild RAW and MIN_DF once (they don't depend on the user) - [CountVectorizer(min_df=...)]")
matrices, build_time = {}, {}
for name, min_df in [("RAW", 1), ("MIN_DF", 2)]:
    start = time.perf_counter()
    matrices[name] = CountVectorizer(token_pattern=r"\S+", lowercase=False, min_df=min_df).fit_transform(recipes["soup"])
    build_time[name] = time.perf_counter() - start
    print(f"{name}: matrix {matrices[name].shape}, built in {build_time[name]:.1f}s")
pause()

# ---------- Iterations ----------

# each iteration = a different random real user with 50-100 liked recipes (seed = iteration number)
pairs = [("RAW", "MIN_DF"), ("RAW", "WHITELIST"), ("MIN_DF", "WHITELIST")]
summary = []
for seed in range(1, ITERATIONS + 1):
    user_id = liked_per_user[liked_per_user.between(50, 100)].sample(1, random_state=seed).index[0]
    favourites, relevant = user_split(user_id)
    print(f"\n========== Iteration {seed}: user {user_id}, {liked_per_user[user_id]} liked, {len(relevant)} relevant ==========")
    print("favourites:", recipes.loc[favourites, "name"].tolist())

    # WHITELIST depends on this user's favourites, so it is rebuilt every iteration
    whitelist = set(token_freq.head(M).index) | set(recipes.loc[favourites, "soup"].str.split().sum())
    start = time.perf_counter()
    matrices["WHITELIST"] = CountVectorizer(token_pattern=r"\S+", lowercase=False,
                                            vocabulary=sorted(whitelist)).fit_transform(recipes["soup"])
    build_time["WHITELIST"] = time.perf_counter() - start

    top_k = {}
    for name, matrix in matrices.items():
        start = time.perf_counter()
        top_k[name] = recommend(matrix, favourites)
        search = time.perf_counter() - start
        summary.append({"iteration": seed, "user": user_id, "variant": name, "dictionary": matrix.shape[1],
                        "build_s": build_time[name], "search_s": search,
                        f"P@{K}": precision_at_k(top_k[name], relevant), f"nDCG@{K}": ndcg_at_k(top_k[name], relevant),
                        "courses": coverage(top_k[name], COURSES), "main_ingredients": coverage(top_k[name], MAIN_INGREDIENTS)})

    lists = pd.DataFrame({name: recipes.loc[ids, "name"].values for name, ids in top_k.items()})
    lists.index += 1
    print(lists)
    print(pd.DataFrame([s for s in summary if s["iteration"] == seed]).set_index("variant")
          [[f"P@{K}", f"nDCG@{K}", "courses", "main_ingredients", "search_s"]])
    print("Jaccard:", {f"{x} vs {y}": round(jaccard(top_k[x], top_k[y]), 2) for x, y in pairs})
    pause()

# ---------- Summary ----------

print(f"\nSummary over {ITERATIONS} users - [.pivot_table()]")
summary = pd.DataFrame(summary)
for metric in [f"P@{K}", f"nDCG@{K}", "courses", "main_ingredients", "search_s"]:
    print(f"\n{metric}:")
    table = summary.pivot_table(index="iteration", columns="variant", values=metric)[list(matrices)]
    table.loc["mean"] = table.mean()
    print(table)

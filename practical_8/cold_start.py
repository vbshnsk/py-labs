import ast
import re
import time

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 60)
pd.set_option("display.max_columns", None)
pd.set_option("display.precision", 3)

LIST_COLUMNS = ["tags", "ingredients", "steps"]
K = 10            # length of the recommendation list
M = 1000          # whitelist: top M tokens by global frequency
LIKED = 4         # rating >= 4 means the user liked the recipe
N_USERS = 100     # users to average the quality metrics over
# category headings of the Food.com tag tree (e.g. "cuisine" on 39% of recipes, the value is "mexican"), they carry no meaning
TAG_HEADINGS = {"preparation", "time_to_make", "course", "main_ingredient", "dietary", "occasion", "cuisine",
                "low_in_something", "equipment", "number_of_servings", "technique", "taste_mood"}
# tag groups for coverage (like genres in practical 7): what kind of dish and what it is mainly made of
COURSES = {"main_dish", "desserts", "side_dishes", "appetizers", "breakfast", "lunch", "brunch", "salads",
           "soups_stews", "breads", "beverages", "snacks", "condiments_etc"}
MAIN_INGREDIENTS = {"meat", "poultry", "seafood", "vegetables", "fruit", "eggs_dairy", "pasta_rice_and_grains", "chocolate"}


def pause():
    input("\nPress Enter for the next step...")


def normalize(token):
    # lower case, every run of spaces/punctuation -> "_": "Olive Oil" -> "olive_oil", "60-minutes-or-less" -> "60_minutes_or_less"
    return re.sub(r"[^a-z0-9]+", "_", token.lower()).strip("_")


def user_split(user_id):
    # favourites = the user's first 3 five-star recipes by date, relevant = their other liked recipes (the right answers)
    user_liked = liked[liked["user_id"] == user_id].sort_values("date")
    favourites = user_liked[user_liked["rating"] == 5]["recipe_id"].head(3).tolist()
    return favourites, set(user_liked["recipe_id"]) - set(favourites)


def recommend(matrix, favourites):
    # profile = mean of the favourites' rows, cosine similarity to every recipe, best K (favourites excluded)
    fav_rows = recipes.index.get_indexer(favourites)
    profile = np.asarray(matrix[fav_rows].mean(axis=0))
    scores = cosine_similarity(profile, matrix).ravel()
    scores[fav_rows] = -1
    best = np.argsort(-scores)[:K]
    return recipes.index[best], scores[best]


def precision_at_k(rec_ids, relevant):
    # share of the K recommendations the user actually liked
    return sum(r in relevant for r in rec_ids) / K


def ndcg_at_k(rec_ids, relevant):
    # like precision, but a hit at position i is worth 1 / log2(i + 2): hits near the top count more;
    # divided by the best possible value (all top positions are hits) so the result is 0..1
    dcg = sum(1 / np.log2(i + 2) for i, r in enumerate(rec_ids) if r in relevant)
    idcg = sum(1 / np.log2(i + 2) for i in range(min(K, len(relevant))))
    return dcg / idcg


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b)


def coverage(rec_ids, group):
    # number of distinct tags of the group (courses / main ingredients) found in the recommended recipes
    return len(set(recipes.loc[rec_ids, "tags"].sum()) & group)


# ---------- Data ----------

# step 1
print("Load recipes and interactions - [pd.read_csv()]")
recipes = pd.read_csv("resources/RAW_recipes.csv")
interactions = pd.read_csv("resources/RAW_interactions.csv")
print(f"recipes {recipes.shape}, interactions {interactions.shape}")
print(recipes.head(3))
print(interactions.head(3))
pause()

# step 2
print("\nCheck format and quality - [.dtypes, .isna().sum(), .duplicated()]")
print(recipes.dtypes)
print(interactions.dtypes)
print("recipes NaN:", recipes.isna().sum()[lambda s: s > 0].to_dict())
print("interactions NaN:", interactions.isna().sum()[lambda s: s > 0].to_dict())
print("duplicate recipe ids:", recipes["id"].duplicated().sum())
print("duplicate user-recipe pairs:", interactions.duplicated(["user_id", "recipe_id"]).sum())
print("ratings:", interactions["rating"].value_counts().sort_index().to_dict())
print("minutes: max", recipes["minutes"].max(), "| 0 minutes", (recipes["minutes"] == 0).sum(),
      "| over a week", (recipes["minutes"] > 7 * 24 * 60).sum())
pause()

print("\nList columns are strings, convert them to lists - [ast.literal_eval]")
print(repr(recipes.loc[0, "tags"][:80]))
for col in LIST_COLUMNS:
    recipes[col] = recipes[col].apply(ast.literal_eval)
print(type(recipes.loc[0, "tags"]), recipes.loc[0, "tags"][:5])
print("empty lists:", {col: int((recipes[col].str.len() == 0).sum()) for col in LIST_COLUMNS})
pause()

print("\nFilter junk: recipes without name, rating 0 (review without rating), interactions of dropped recipes - [boolean masks]")
before = len(recipes), len(interactions)
recipes = recipes.dropna(subset=["name"])
interactions = interactions[(interactions["rating"] > 0) & interactions["recipe_id"].isin(recipes["id"])]
print(f"recipes removed: {before[0] - len(recipes)}, interactions removed: {before[1] - len(interactions)}")
pause()

print("\nNormalize tokens: lower case, spaces/punctuation -> '_' - [re.sub()]")
for col in ["tags", "ingredients"]:
    recipes[col] = recipes[col].apply(lambda tokens: [normalize(t) for t in tokens])
print(recipes[["name", "tags", "ingredients"]].head())
pause()

# step 3
print("\nBuild the soup: tags (no headings) + ingredients - [list concat + ' '.join()]")
# tags        - cuisine, course, diet, occasion, time: what kind of dish it is
# ingredients - what is inside, the strongest signal of taste
# skipped: name (free-form title, words like "best"/"easy"/"moms" and author names; the dish type is already in tags),
#          steps/description (long free text, generic words like "stir"/"add", description missing for ~5k recipes),
#          review (users' opinion, not the recipe itself), minutes/nutrition (numbers, not tokens; minutes has junk)
recipes["soup"] = (
    recipes["tags"].apply(lambda tokens: [t for t in tokens if t not in TAG_HEADINGS])
    + recipes["ingredients"]
).str.join(" ")
recipes = recipes.set_index("id")
print(recipes[["name", "soup"]].head())
print("tokens per soup:", recipes["soup"].str.split().str.len().describe().round(1).to_dict())
pause()

# step 4
print("\nVectorize with CountVectorizer: one column per token, value = count in the soup - [CountVectorizer().fit_transform()]")
# The result is a sparse matrix: one row per recipe, one column per token of the dictionary (all distinct tokens),
# value = how many times the token is in the recipe's soup. A recipe has ~24 tokens out of tens of thousands,
# so almost all values are 0 and only the non-zero ones are stored. Each row is the recipe's vector, and
# recipes with similar vectors (many shared tokens) are similar dishes -> compared later with cosine similarity.
# tokens are already normalized and joined by spaces, so split on whitespace only and don't lowercase again
vectorizer = CountVectorizer(token_pattern=r"\S+", lowercase=False)
sample = vectorizer.fit_transform(recipes["soup"].head(3))
print(pd.DataFrame(sample.toarray(), columns=vectorizer.get_feature_names_out(), index=recipes.index[:3]).T.head(15))
pause()

# ---------- Soup variants ----------

# step 5
print("\nImitate a user: a real user with 50-100 liked recipes, first 3 five-star recipes by date = favourites - [.sample()]")
# picked before the variants because the whitelist needs the favourites' tokens
liked = interactions[interactions["rating"] >= LIKED]
liked_per_user = liked.groupby("user_id").size()
user_id = liked_per_user[liked_per_user.between(50, 100)].sample(1, random_state=42).index[0]
favourites, relevant = user_split(user_id)
print(f"user {user_id}: {liked_per_user[user_id]} liked recipes, {len(relevant)} relevant after taking 3 favourites")
print(recipes.loc[favourites, ["name", "soup"]])
pause()

print("\nBuild the 3 soup variants - [CountVectorizer(min_df=...) / CountVectorizer(vocabulary=...)]")
# RAW       - min_df=1: every token gets a column, including one-off typos and rare ingredients (biggest dictionary)
# MIN_DF    - min_df=2: drop tokens found in only 1 recipe, they can never match another recipe anyway
# WHITELIST - controlled vocabulary: top M tokens by global frequency + all tokens of the favourites
#             (smallest dictionary, rare tokens are lost unless the user's favourites have them)
token_freq = recipes["soup"].str.split().explode().value_counts()
whitelist = set(token_freq.head(M).index) | set(recipes.loc[favourites, "soup"].str.split().sum())
vectorizers = {
    "RAW": CountVectorizer(token_pattern=r"\S+", lowercase=False, min_df=1),
    "MIN_DF": CountVectorizer(token_pattern=r"\S+", lowercase=False, min_df=2),
    "WHITELIST": CountVectorizer(token_pattern=r"\S+", lowercase=False, vocabulary=sorted(whitelist)),
}
matrices, build_time = {}, {}
for name, vec in vectorizers.items():
    start = time.perf_counter()
    matrices[name] = vec.fit_transform(recipes["soup"])
    build_time[name] = time.perf_counter() - start
    print(f"{name}: matrix {matrices[name].shape}, built in {build_time[name]:.1f}s")
pause()

# ---------- Cold start ----------

# step 6
print("\nUser profile = mean of the favourites' vectors, rank all other recipes by cosine similarity - [.mean() + cosine_similarity()]")
top_k, search_time = {}, {}
for name, matrix in matrices.items():
    start = time.perf_counter()
    rec_ids, scores = recommend(matrix, favourites)
    search_time[name] = time.perf_counter() - start
    top_k[name] = pd.DataFrame({"name": recipes.loc[rec_ids, "name"], "score": scores})
    top_k[name]["liked"] = top_k[name].index.isin(relevant)
    print(f"\n{name} top {K} (search {search_time[name]:.2f}s):")
    print(top_k[name])
    pause()

# ---------- Metrics ----------

# step 7
print(f"\nQuality and resource metrics for user {user_id} - [Precision@K, nDCG@K, .nnz, time.perf_counter()]")
# dictionary size = number of columns (distinct tokens), density = share of non-zero values in the matrix
metrics = pd.DataFrame({
    name: {
        "dictionary": matrix.shape[1],
        "density": matrix.nnz / (matrix.shape[0] * matrix.shape[1]),
        "build_s": build_time[name],
        "search_s": search_time[name],
        f"P@{K}": precision_at_k(top_k[name].index, relevant),
        f"nDCG@{K}": ndcg_at_k(top_k[name].index, relevant),
    }
    for name, matrix in matrices.items()
}).T
print(metrics.to_string(formatters={"dictionary": "{:.0f}".format, "density": "{:.6f}".format}))
pause()

print(f"\nAverage quality over {N_USERS} users with 50-100 liked recipes - [loop over users + .mean()]")
# one user is too noisy (0 hits out of 231k recipes is normal), so repeat the cold start for many users.
# the whitelist depends on the user's favourites; instead of refitting CountVectorizer for each user,
# take the RAW matrix columns of the whitelist tokens (same counts, much faster)
raw_vocab = vectorizers["RAW"].vocabulary_
raw_csc = matrices["RAW"].tocsc()
top_cols = [raw_vocab[t] for t in token_freq.head(M).index]
users = liked_per_user[liked_per_user.between(50, 100)].sample(N_USERS, random_state=42).index
rows = []
for uid in users:
    favs, rel = user_split(uid)
    if len(favs) < 3:  # needs 3 five-star recipes
        continue
    fav_cols = [raw_vocab[t] for t in set(recipes.loc[favs, "soup"].str.split().sum())]
    user_matrices = {
        "RAW": matrices["RAW"],
        "MIN_DF": matrices["MIN_DF"],
        "WHITELIST": raw_csc[:, sorted(set(top_cols) | set(fav_cols))].tocsr(),
    }
    recs = {name: recommend(m, favs)[0] for name, m in user_matrices.items()}
    for name, rec_ids in recs.items():
        rows.append({"user": uid, "variant": name, f"P@{K}": precision_at_k(rec_ids, rel),
                     f"nDCG@{K}": ndcg_at_k(rec_ids, rel), "hit": precision_at_k(rec_ids, rel) > 0,
                     "courses": coverage(rec_ids, COURSES), "main_ingredients": coverage(rec_ids, MAIN_INGREDIENTS),
                     "recs": list(rec_ids)})
per_user = pd.DataFrame(rows)
print(f"users used: {per_user['user'].nunique()}")
print(per_user.groupby("variant")[[f"P@{K}", f"nDCG@{K}", "hit"]].mean().reindex(list(matrices))
      .rename(columns={"hit": "users_with_a_hit"}))
pause()

# ---------- Comparison ----------

# step 8
print(f"\nCompare the ranked lists of user {user_id}: Jaccard between top {K}s - [len(a & b) / len(a | b)]")
pairs = [("RAW", "MIN_DF"), ("RAW", "WHITELIST"), ("MIN_DF", "WHITELIST")]
for x, y in pairs:
    print(f"{x} vs {y}: {jaccard(top_k[x].index, top_k[y].index):.2f}")
print(f"\naverage over {per_user['user'].nunique()} users:")
lists = per_user.pivot(index="user", columns="variant", values="recs")
for x, y in pairs:
    print(f"{x} vs {y}: {lists.apply(lambda r: jaccard(r[x], r[y]), axis=1).mean():.2f}")
pause()

print(f"\nCoverage: distinct courses ({len(COURSES)}) and main ingredients ({len(MAIN_INGREDIENTS)}) in the top {K} - [set of tags & group]")
for name in matrices:
    print(f"{name} (user {user_id}): {coverage(top_k[name].index, COURSES)} courses, "
          f"{coverage(top_k[name].index, MAIN_INGREDIENTS)} main ingredients")
print(f"\naverage over {per_user['user'].nunique()} users:")
print(per_user.groupby("variant")[["courses", "main_ingredients"]].mean().reindex(list(matrices)))
print("\ncatalog coverage: distinct recipes recommended to all users together (of", len(recipes), "):")
print(per_user.groupby("variant")["recs"].sum().apply(lambda r: len(set(r))).reindex(list(matrices)))
pause()

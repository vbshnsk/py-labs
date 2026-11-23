import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 60)
pd.set_option("display.max_columns", None)
pd.set_option("display.precision", 3)

BETA = 5
GENRES = {
    "fantasy": ["fantasy"],
    "romance": ["romance"],
    "sci-fi": ["science-fiction", "sci-fi"],
    "mystery": ["mystery"],
    "thriller": ["thriller"],
    "horror": ["horror"],
    "historical-fiction": ["historical-fiction"],
    "classics": ["classics"],
    "non-fiction": ["non-fiction", "nonfiction"],
    "young-adult": ["young-adult", "ya"],
    "contemporary": ["contemporary"],
    "paranormal": ["paranormal"],
    "dystopian": ["dystopian", "dystopia"],
    "biography": ["biography", "memoir"],
    "poetry": ["poetry"],
    "philosophy": ["philosophy"],
    "humor": ["humor", "humour"],
    "christian": ["christian", "religion"],
    "self-help": ["self-help"],
}
COMICS = "comic|graphic-novel|manga"


def book_stats(ratings):
    # tot      - total number of ratings the book got (how many users rated it)
    # pos      - number of positive ratings (4 or 5 stars)
    # mean     - average rating (1-5)
    # pos_rate - share of positive ratings, pos / tot
    # smoothed - pos_rate pulled toward 0.5 for books with few ratings, (pos + BETA) / (tot + 2 * BETA)
    stats = ratings.groupby("book_id")["rating"].agg(
        tot="size", pos=lambda r: (r >= 4).sum(), mean="mean"
    )
    stats["pos_rate"] = stats["pos"] / stats["tot"]
    stats["smoothed"] = (stats["pos"] + BETA) / (stats["tot"] + 2 * BETA)
    return stats.join(books.set_index("book_id")["title"])


def pause():
    input("\nPress Enter for the next step...")


def jaccard(a, b):
    # Jaccard similarity of two tops: shared books / all distinct books in either top.
    # 1.0 = same books, 0.0 = no books in common (order inside the top is ignored).
    # For two top 10s: 0.82 = 9 shared books, 0.54 = 7, 0.43 = 6, 0.05 = 1.
    a, b = set(a.index), set(b.index)
    return len(a & b) / len(a | b)


# ---------- Data ----------

# step 1
print("Load the goodbooks-10k data - [pd.read_csv()]")
books = pd.read_csv("resources/books.csv")
ratings = pd.read_csv("resources/ratings.csv")
book_tags = pd.read_csv("resources/book_tags.csv")
tags = pd.read_csv("resources/tags.csv")
print(f"books {books.shape}, ratings {ratings.shape}, book_tags {book_tags.shape}, tags {tags.shape}")
pause()

# step 2
print("\nCombine datasets: ratings + books, book_tags + tags + books - [.merge()]")
rated_books = ratings.merge(books[["book_id", "title"]], on="book_id")
book_tags = book_tags.merge(tags, on="tag_id").merge(
    books[["book_id", "goodreads_book_id"]], on="goodreads_book_id"
)
print(rated_books.head())
print(book_tags.head())
pause()

# step 3
print("\nPer book: tot, pos (rating >= 4), mean, pos_rate - [.groupby().agg()]")
stats = book_stats(ratings)
print(stats.head())
pause()

# step 4
print("\nFilter junk: non-positive ids, ratings outside 1-5, NaN, duplicates, non-positive tag counts - [boolean masks]")
before = len(ratings), len(book_tags)
ratings = ratings.dropna().drop_duplicates(["user_id", "book_id"])
ratings = ratings[(ratings["user_id"] > 0) & (ratings["book_id"] > 0) & ratings["rating"].between(1, 5)]
book_tags = book_tags[(book_tags["count"] > 0) & (book_tags["book_id"] > 0)]
stats = book_stats(ratings)
print(f"ratings removed: {before[0] - len(ratings)}, book_tags removed: {before[1] - len(book_tags)}")
print(stats.describe())
pause()

# ---------- Rankings ----------

# step 5
print("\nA: top 10 by mean - [.nlargest(10, 'mean')]")
a = stats.nlargest(10, "mean")
print(a)
pause()

print("\nB: top 10 by mean with tot > 100 - [stats[stats['tot'] > 100].nlargest()]")
b = stats[stats["tot"] > 100].nlargest(10, "mean")
print(b)
print(f"(books with tot > 100: {(stats['tot'] > 100).sum()} of {len(stats)})")
pause()

print("\nB1000: top 10 by mean with tot > 1000 - [stats[stats['tot'] > 1000].nlargest()]")
b1000 = stats[stats["tot"] > 1000].nlargest(10, "mean")
print(b1000)
pause()

print(f"\nC: top 10 by smoothed (pos + {BETA}) / (tot + {2 * BETA}) - [.nlargest(10, 'smoothed')]")
c = stats.nlargest(10, "smoothed")
print(c)
pause()

# step 6
print("\nDrop every book with any comics tag and rebuild the tops - [.str.contains()]")
comic_ids = book_tags.loc[book_tags["tag_name"].str.contains(COMICS), "book_id"].unique()
no_comics = stats.drop(comic_ids, errors="ignore")
print(f"comics books dropped: {len(comic_ids)}")
pause()
tops = {
    "A": (a, no_comics.nlargest(10, "mean")),
    "B": (b, no_comics[no_comics["tot"] > 100].nlargest(10, "mean")),
    "B1000": (b1000, no_comics[no_comics["tot"] > 1000].nlargest(10, "mean")),
    "C": (c, no_comics.nlargest(10, "smoothed")),
}
for name, (top, top_nc) in tops.items():
    print(f"\n{name} without comics:")
    print(top_nc)
    print("  out:", top.loc[top.index.difference(top_nc.index), "title"].tolist())
    print("  in: ", top_nc.loc[top_nc.index.difference(top.index), "title"].tolist())
    pause()

# ---------- Comparison ----------

# step 7
print("\nJaccard between tops - [len(a & b) / len(a | b)]")
for x, y in [("A", "B"), ("A", "C"), ("B", "C"), ("B1000", "C")]:
    print(f"{x} vs {y}: {jaccard(tops[x][0], tops[y][0]):.2f}")
pause()

# step 8
print("\nGenre coverage of each top 10 without comics: main genre = genre tag with most votes - [.map() + .groupby().idxmax()]")
tag_to_genre = {tag: genre for genre, names in GENRES.items() for tag in names}
book_tags["genre"] = book_tags["tag_name"].map(tag_to_genre)
genre_votes = book_tags.dropna(subset=["genre"]).groupby(["book_id", "genre"])["count"].sum().reset_index()
main_genre = genre_votes.loc[genre_votes.groupby("book_id")["count"].idxmax()].set_index("book_id")["genre"]
all_genres = genre_votes.groupby("book_id")["genre"].unique()
for name, (_, top_nc) in tops.items():
    main = main_genre.reindex(top_nc.index).dropna()
    tagged = all_genres.reindex(top_nc.index).dropna().explode().nunique()
    print(f"{name}: {main.nunique()} main genres {main.value_counts().to_dict()} | {tagged} genres among all tags")

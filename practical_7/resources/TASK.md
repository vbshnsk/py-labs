# 7. The Simple Recommender System

Due December 11, 2026 12:59 AM

Data source: https://github.com/zygmuntz/goodbooks-10k

1. Download the data.
2. Data preparation:
   - combine datasets
3. For each book, calculate:
   - the total number of ratings `tot`;
   - the number of positive ratings `pos` (i.e. ratings ≥ 4);
   - the average rating `mean`;
   - the proportion of positive ratings `pos_rate = pos/tot`.
4. Filter out obvious junk entries (zero/negative IDs, etc.).
5. Build 3 ratings:
   - Average rating by mean, take the top 10.
   - Average rating with a rating threshold (e.g., greater than 100)
   - Average smoothed rating `(pos+β)/(tot+2β)`, where β is a small number (e.g., 5)
6. Try removing comics from the lists and evaluate the changes.
7. Compare the lists using the Jaccard metric. The lists should be compared in pairs (A vs B), (A vs C), (B vs C). How much do the lists change?
8. Analyse genre coverage:
   - Using `book_tags.csv` and `tags.csv`, determine the genres for each book (e.g., 'fantasy', 'romance', 'sci-fi').
   - For each top 10 ranking, count how many different genres it covers. For example: there are 10 books in the top, but all of them are from the same genre → coverage is low. If there are 10 books in the top and they are from 7 different genres → coverage is high.
9. Draw conclusions (in writing):
   - how the threshold affects;
   - how smoothing changes the situation;
   - which genres prevail in different variants.

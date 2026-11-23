# Conclusions

We prepare the dataset and then try to figure out the top 10 best rated books.
For that we build the top 10 in the following ways:
    A. top 10 by mean rating
    B. top 10 by mean rating, excl. books with 100 or fewer ratings (removing junk data)
    B1000. same as B, excl. books with 1000 or fewer ratings (even more junk data removed)
    C. top 10 by smoothed rating (using virtual ratings to dampen junk data)

Then we used the Jaccard metric (shared books / all distinct books) to compare the lists' similarity:

| Pair | Jaccard | Shared books |
|---|---|---|
| A vs B | 0.82 | 9 of 10 |
| A vs C | 0.54 | 7 of 10 |
| B vs C | 0.54 | 7 of 10 |
| B1000 vs C | 0.05 | 1 of 10 |

This is how fixing up the data has affected the results:

## Threshold

- A low threshold (100) has almost no effect: almost every book has more than 100 ratings, so B keeps 9 of A's 10 books (mostly Calvin and Hobbes collections)
- A high threshold (1000) changes the list completely: only widely read books remain, mostly big fantasy series

## Smoothing

- Smoothing lowers the score of books with few ratings instead of cutting them off, so the top changes by about a third (7 of 10 books shared with A and B)
- It favours books that have both many ratings and a high share of positive ones (Words of Radiance, Saga Vol. 2) over small niche ones (ESV Study Bible)

## Genres

Counted on the tops without comics.

- Low coverage everywhere: 2-5 main genres per top 10 (A and B 5, C 3, B1000 2)
- Fantasy prevails in every variant (5 of 10 in A/B, 7 in C, 9 in B1000)
- A/B add Christian and poetry, C adds non-fiction, B1000 is almost only fantasy

# Bonus: iterations with different random users

`bonus.py` repeats the cold start for 5 different random real users (50-100 liked recipes each, seeds 1-5).
For each user: first 3 five-star recipes = favourites, top 10 for RAW / MIN_DF / WHITELIST.

| Iteration | User | Favourites | Top 10 is mostly |
|---|---|---|---|
| 1 | 663171 | roast turkey, chicken with onions, ziti with sausage | roast turkey and baked chicken |
| 2 | 308961 | sausage casserole, cinnamon tea cake, brownies | brownies, cookies, cakes |
| 3 | 296085 | duck confit pasta, cheese curds, salsa | Italian pasta and chicken |
| 4 | 738454 | cauliflower, candied almonds, cinnamon rolls | sweet potatoes, yams, sweet side dishes |
| 5 | 1458294 | peanut butter sandwiches, banana wrap, hot chocolate | peanut butter / banana breakfasts |

## Quality

- P@10 and nDCG@10 are 0 for every user and every variant
- But the lists look sensible: they clearly follow the favourites
- So the metric only says the user hasn't rated these recipes, not that they are bad recommendations

## Profile

- Coherent favourites (iteration 5: all peanut butter / banana) give a very on-theme list
- Mixed favourites get dominated by the majority (iteration 2: 2 of 3 are desserts → only desserts, the casserole is lost)

## Variants

- RAW vs MIN_DF: Jaccard 0.82-1.0, almost the same lists every time
- WHITELIST shares ~6 of 10 with them (Jaccard 0.43-0.54) but stays on the same theme
- Coverage is the same on average: 3.0 courses, 2.8 main ingredients for every variant
- Search: RAW 0.09s, MIN_DF 0.08s, WHITELIST 0.03s every time

## Finding

- The results from the main script hold for every user: variants give the same quality, WHITELIST is ~3x faster
- With 3 favourites, the lists follow the favourites' theme closely, so a cold-start user gets "more of the same"

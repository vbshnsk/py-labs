# Conclusions

## Soup

- Fields: tags (no category headings) + ingredients, ~20 tokens per recipe
- Skipped: name (free-form title, dish type is already in tags), steps/description (long generic text), review (opinion, not the recipe), minutes/nutrition (numbers)

## Resources

| Variant | Dictionary | Density | Build | Search |
|---|---|---|---|---|
| RAW | 15304 | 0.13% | 1.3s | 0.10s |
| MIN_DF | 11735 | 0.17% | 1.4s | 0.08s |
| WHITELIST | 1002 | 1.9% | 1.2s | 0.03s |

- MIN_DF drops ~a quarter of the dictionary, WHITELIST cuts it ~15x and searches ~3x faster

## Quality

- How it's measured: real users with 50-100 liked recipes; 3 are shown as favourites, the other ~48 are hidden and count as right answers
- P@10 = share of the top 10 that are hidden liked recipes, nDCG@10 = the same but hits near the top count more
- Very low and equal for all variants: P@10 0.003, nDCG@10 0.003 over 100 users (3 users of 100 got a hit)
- Why so low: ~48 right answers among 231k recipes (~1000x better than random still rounds to 0); unrated recipes count as misses even if the user might like them; 3 favourites can't cover the user's broad taste (the cold start problem)
- The whitelist does not lose quality

## Finding

- Absolute quality values say little, the comparison between variants on the same users matters
- All 3 variants give the same quality, so a smaller dictionary (MIN_DF, WHITELIST) costs nothing and is faster: WHITELIST is the best trade-off

## Lists

- RAW vs MIN_DF are almost identical (Jaccard 0.96): tokens found in 1 recipe can't match others
- WHITELIST shares about 7-8 of 10 with them (Jaccard 0.62)
- Coverage is about the same for all: ~3.3 courses and ~3.4 main ingredients per top 10, ~975 distinct recipes across 100 users

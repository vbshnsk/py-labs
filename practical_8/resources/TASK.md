# 8. The Cold Start

Due December 11, 2026 12:59 AM

1. You will need the Food.com Recipes & Interactions dataset - `RAW_recipes.csv` and `RAW_interactions.csv`. https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions
2. Prepare the data. Check its format and quality. Key fields: `name`, `id`, `tags`, `ingredients`, `steps`, `description` (recipes) and `user_id`, `recipe_id`, `rating`, `review` (interactions). Convert columns and rows into lists where necessary, normalise tokens for soup - lower case, replace spaces, remove punctuation.
3. Select the fields that you think are necessary for soup. Justify your choice. Create a new field with 'soup (porridge) metadata'.
4. Use `CountVectorizer` for vectorisation.
5. You will have 3 types of soup from metadata to work with. Implement them all and compare the results:
   1. RAW. `CountVectorizer(min_df=1)` - all tokens are available
   2. min_df - with token truncation, with a frequency below a certain threshold. E.g., 2.
   3. Controlled vocabulary. Build a list of acceptable tokens (a so-called whitelist). This is the top M tokens by global frequency + tokens from the user's 'favourite' recipes
6. Let's work on the 'Cold Start' option. Imitate a user and select 3 favourite recipes.
   - Get the soup vectors of these recipes and build a user profile as an average
   - Build a ranked list of recommendations using the cosine similarity between the profile and other recipes. Please note that the accuracy of the recommendations will be better if you process the entire dataset. However, this requires a lot of resources — find the right balance for your work machine.
   - Do this for each of the 3 types of soup.
7. Calculate the quality and resource usage metrics for each option (Precision@K, nDCG@K; dictionary size, matrix density, construction and search time).
8. Compare the metrics of the variants with each other. Also, compare the ranked lists with each other, including by 'coverage' (similar to the previous lab work).

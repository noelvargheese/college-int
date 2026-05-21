import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

# Load dataset
csv_path = os.path.join(os.path.dirname(__file__), "anime.csv")
df = pd.read_csv(csv_path)

# Create a simple tag field for recommendation
# This uses genre, popularity, and anime name tokens.
if "popularity" not in df.columns:
    df["popularity"] = "Unknown"

df["tags"] = (
    df["genre"].fillna("") + " " +
    df["popularity"].fillna("") + " " +
    df["name"].fillna("")
)

# Vectorize text tags
cv = CountVectorizer(max_features=200)
vectors = cv.fit_transform(df["tags"]).toarray()

# Compute similarity matrix
similarity = cosine_similarity(vectors)

# Save models
model_dir = os.path.join(os.path.dirname(__file__), "model")
os.makedirs(model_dir, exist_ok=True)

joblib.dump(similarity, os.path.join(model_dir, "similarity.pkl"))
joblib.dump(df, os.path.join(model_dir, "anime_list.pkl"))

print("Recommendation model trained!")

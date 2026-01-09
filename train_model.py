import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

# Load dataset
df = pd.read_csv("cleaned_dataset.csv")

# Clean and prepare
df.dropna(subset=["text", "label"], inplace=True)
df["label"] = df["label"].astype(int)

# Split data
X_train, X_test, y_train, y_test = train_test_split(df["text"], df["label"], test_size=0.2, random_state=42)

# Pipeline: TF-IDF + Classifier
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', max_features=10000)),
    ('clf', LogisticRegression(max_iter=300))
])

# Train
pipeline.fit(X_train, y_train)

# Evaluate
accuracy = pipeline.score(X_test, y_test)
print(f"\n✅ Model trained successfully with accuracy: {accuracy:.2%}")

# Save model
joblib.dump(pipeline, "phishing_model.pkl")
print("💾 Model saved as phishing_model.pkl")

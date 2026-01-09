import pandas as pd
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Load dataset
df = pd.read_csv("ml_model/phishing_dataset.csv")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label"], test_size=0.2, random_state=42
)

# Pipeline
model_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', max_features=1000)),
    ('clf', LogisticRegression(max_iter=1000, random_state=42))
])

# Train model
model_pipeline.fit(X_train, y_train)

# Evaluate
y_pred = model_pipeline.predict(X_test)
report = classification_report(y_test, y_pred)
print("✅ Retraining Complete")
print(report)

# Save model
os.makedirs("ml_model", exist_ok=True)
joblib.dump(model_pipeline, "ml_model/phishing_model.pkl")
print("✅ Model saved to ml_model/phishing_model.pkl")

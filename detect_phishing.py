import joblib

# Load the trained model
model = joblib.load("phishing_model.pkl")

# Sample input (replace with user input or test examples)
sample_text = input("Enter the message to check: ")

# Simple preprocessing (just lowercase for now)
features = [sample_text.lower()]

# Predict
prediction = model.predict(features)

# Output result
if prediction[0] == 1:
    print("⚠️ This message is likely a PHISHING attempt.")
else:
    print("✅ This message seems SAFE.")

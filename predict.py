import joblib
from urllib.parse import urlparse

# Load trained model
model = joblib.load("phishing_model.pkl")


# Feature extraction function
def extract_features(url):
    parsed_url = urlparse(url)

    return [[
        len(url),
        url.count("."),
        url.count("/"),
        url.count("-"),
        sum(char.isdigit() for char in url),
        url.count("@"),
        1 if parsed_url.scheme == "https" else 0
    ]]


# Get URL from user
url = input("Enter URL: ")

# Extract features
features = extract_features(url)

# Predict
prediction = model.predict(features)[0]

# Display result
if prediction == 1:
    print("⚠️ Phishing URL Detected!")
else:
    print("✅ Legitimate URL")
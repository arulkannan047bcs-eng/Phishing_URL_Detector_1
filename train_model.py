import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load dataset
df = pd.read_csv("dataset.csv")


# Feature extraction function
def extract_features(url):
    from urllib.parse import urlparse

    parsed_url = urlparse(url)

    return [
        len(url),
        url.count("."),
        url.count("/"),
        url.count("-"),
        sum(char.isdigit() for char in url),
        url.count("@"),
        1 if parsed_url.scheme == "https" else 0
    ]


# Create features
X = df["url"].apply(extract_features).tolist()

# Target
y = df["label"]


# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# Create Random Forest model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


# Train model
model.fit(X_train, y_train)


# Prediction
y_pred = model.predict(X_test)


# Accuracy
accuracy = accuracy_score(y_test, y_pred)

print("Model Accuracy:", accuracy)


# Save model
joblib.dump(model, "phishing_model.pkl")

print("Model saved successfully!")
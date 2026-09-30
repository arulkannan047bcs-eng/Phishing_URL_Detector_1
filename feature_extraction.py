import pandas as pd
from urllib.parse import urlparse

# Load dataset
df = pd.read_csv("dataset.csv")

# Function to extract features
def extract_features(url):
    parsed_url = urlparse(url)

    features = {
        "url_length": len(url),
        "dot_count": url.count("."),
        "slash_count": url.count("/"),
        "hyphen_count": url.count("-"),
        "digit_count": sum(char.isdigit() for char in url),
        "at_count": url.count("@"),
        "https": 1 if parsed_url.scheme == "https" else 0
    }

    return features

# Apply feature extraction
features = df["url"].apply(extract_features)

# Convert features into DataFrame
features_df = pd.DataFrame(features.tolist())

# Add label
features_df["label"] = df["label"]

# Display result
print(features_df)
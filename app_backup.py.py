import streamlit as st
import joblib
from urllib.parse import urlparse

# Load trained model
model = joblib.load("phishing_model.pkl")


# Feature extraction
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


# Page configuration
st.set_page_config(
    page_title="Phishing URL Detector",
    page_icon="🔐",
    layout="centered"
)


# Custom CSS
st.markdown("""
<style>

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    margin-bottom: 30px;
}

.result-box {
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    font-size: 22px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# Title
st.markdown(
    '<div class="main-title">🔐 Phishing URL Detector</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Machine Learning Based Website URL Security Checker</div>',
    unsafe_allow_html=True
)


# URL input
url = st.text_input(
    "🌐 Enter Website URL",
    placeholder="https://example.com"
)


# Check button
if st.button("🔍 Check URL", use_container_width=True):

    if not url.strip():
        st.warning("Please enter a website URL.")

    else:

        features = extract_features(url)

        prediction = model.predict(features)[0]

        st.subheader("🔎 Analysis Result")

        if prediction == 1:
            st.error(
                "⚠️ Phishing URL Detected!\n\n"
                "This URL has suspicious characteristics."
            )

        else:
            st.success(
                "✅ Legitimate URL\n\n"
                "This URL appears legitimate based on the trained model."
            )


# Footer
st.markdown("---")

st.caption(
    "Cybersecurity Project | Phishing URL Detection using Machine Learning"
)
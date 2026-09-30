import streamlit as st
import joblib
import hashlib
import os
import ipaddress
from urllib.parse import urlparse

from database.database import get_connection, create_tables


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="PhishGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700;800;900&family=Rajdhani:wght@400;500;600;700&display=swap');

:root {
    --bg: #030712;
    --panel: rgba(7, 16, 31, 0.82);
    --panel2: rgba(10, 27, 49, 0.72);
    --cyan: #00eaff;
    --blue: #1688ff;
    --text: #e9f7ff;
    --muted: #8aa7bd;
    --line: rgba(0, 234, 255, 0.20);
}

html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; }
.stApp {
    background:
        radial-gradient(circle at 75% 15%, rgba(0,234,255,.18), transparent 28%),
        radial-gradient(circle at 15% 80%, rgba(22,136,255,.13), transparent 30%),
        linear-gradient(135deg, rgba(2,7,18,.98), rgba(3,13,27,.94)),
        url('assets/theme_bg.png') center/cover fixed no-repeat;
    color: var(--text);
}
.stApp::before {
    content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background: linear-gradient(rgba(0,234,255,.025) 1px, transparent 1px), linear-gradient(90deg, rgba(0,234,255,.025) 1px, transparent 1px);
    background-size: 42px 42px;
}
.block-container { padding: 2rem 3rem 4rem; max-width: 1500px; position: relative; z-index: 1; }

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(2,10,22,.97), rgba(4,20,36,.97));
    border-right: 1px solid rgba(0,234,255,.25);
    box-shadow: 8px 0 35px rgba(0,0,0,.35);
}
section[data-testid="stSidebar"] > div { padding: 1.4rem 1rem; }
.sidebar-title, .main-title, .section-title, .login-title {
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 1px;
    text-shadow: 0 0 18px rgba(0,234,255,.35);
}
.sidebar-title { font-size: 27px; font-weight: 900; color: var(--cyan); }
.sidebar-subtitle { color: #7398b2; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; }
section[data-testid="stSidebar"] hr { border-color: rgba(0,234,255,.16); }
section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 8px; }
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(7,21,38,.72); border: 1px solid rgba(0,234,255,.10);
    border-radius: 12px; padding: 12px 14px; margin-bottom: 4px;
    transition: .22s ease; color: #b8d7e8;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    border-color: var(--cyan); background: rgba(0,234,255,.09); transform: translateX(3px);
    box-shadow: 0 0 18px rgba(0,234,255,.12);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(0,234,255,.16), rgba(22,136,255,.06));
    border-color: var(--cyan); color: #fff; box-shadow: inset 3px 0 var(--cyan), 0 0 20px rgba(0,234,255,.10);
}

/* HEADINGS */
.main-title { font-size: clamp(34px, 4vw, 58px); font-weight: 900; color: #f3fbff; margin-bottom: 2px; }
.main-title::first-letter { color: var(--cyan); }
.main-subtitle { color: #82a9c0; font-size: 18px; letter-spacing: 1px; margin-bottom: 25px; }
.section-title { font-size: clamp(26px, 3vw, 40px); font-weight: 900; color: #f2fbff; }
.section-text { color: var(--muted); font-size: 17px; }

/* GLASS CARDS */
.card, .analysis-card, .report-card {
    background: linear-gradient(145deg, rgba(8,25,45,.88), rgba(3,12,25,.78));
    border: 1px solid var(--line); border-radius: 18px; padding: 24px;
    box-shadow: 0 15px 45px rgba(0,0,0,.28), inset 0 0 25px rgba(0,234,255,.025);
    margin-bottom: 18px; position: relative; overflow: hidden;
    transition: .25s ease;
}
.card::before, .analysis-card::before, .report-card::before {
    content:""; position:absolute; left:0; top:0; width:55px; height:2px; background:var(--cyan); box-shadow:0 0 14px var(--cyan);
}
.card:hover, .analysis-card:hover, .report-card:hover { transform: translateY(-3px); border-color: rgba(0,234,255,.45); box-shadow: 0 18px 50px rgba(0,0,0,.4), 0 0 25px rgba(0,234,255,.08); }

/* METRICS */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(8,27,48,.9), rgba(3,13,26,.86));
    border: 1px solid rgba(0,234,255,.22); border-radius: 16px; padding: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,.28); transition:.2s;
}
div[data-testid="stMetric"]:hover { border-color: var(--cyan); box-shadow: 0 0 22px rgba(0,234,255,.12); }
div[data-testid="stMetricLabel"] { color:#7fa5bb !important; }
div[data-testid="stMetricValue"] { color:#f2fbff !important; font-family:'Orbitron',sans-serif; }

/* INPUTS */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    background: rgba(3,13,26,.86) !important; color:#eafaff !important;
    border:1px solid rgba(0,234,255,.22) !important; border-radius:12px !important;
    min-height:48px; box-shadow: inset 0 0 16px rgba(0,0,0,.25);
}
.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus { border-color:var(--cyan) !important; box-shadow:0 0 0 1px var(--cyan), 0 0 18px rgba(0,234,255,.12) !important; }
label, .stTextInput label, .stTextArea label { color:#b7d5e5 !important; font-weight:600 !important; }

/* BUTTONS */
.stButton > button {
    min-height: 46px; border-radius: 11px; border:1px solid rgba(0,234,255,.35);
    background: linear-gradient(135deg, rgba(0,234,255,.13), rgba(22,136,255,.12));
    color:#eaffff; font-family:'Rajdhani',sans-serif; font-weight:800; letter-spacing:.6px;
    transition:.22s ease; box-shadow:0 0 12px rgba(0,234,255,.05);
}
.stButton > button:hover { border-color:var(--cyan); color:#fff; transform:translateY(-2px); box-shadow:0 0 24px rgba(0,234,255,.18); background:linear-gradient(135deg, rgba(0,234,255,.22), rgba(22,136,255,.18)); }
.stButton > button:active { transform:translateY(0); }

/* ALERTS / TABLES */
div[data-testid="stAlert"] { border-radius:12px; background:rgba(6,22,39,.86); border:1px solid rgba(0,234,255,.18); }
div[data-testid="stDataFrame"] { border:1px solid rgba(0,234,255,.18); border-radius:14px; overflow:hidden; }
.stTabs [data-baseweb="tab-list"] { gap:6px; background:rgba(4,14,27,.75); padding:6px; border-radius:12px; }
.stTabs [data-baseweb="tab"] { color:#83a9bf; border-radius:9px; }
.stTabs [aria-selected="true"] { color:var(--cyan) !important; background:rgba(0,234,255,.09); }

/* LOGIN */
.login-wrapper { max-width: 470px; margin: 7vh auto 30px; }
.login-dark-card {
    background: linear-gradient(145deg, rgba(5,20,36,.95), rgba(2,9,19,.96));
    border:1px solid rgba(0,234,255,.30); border-radius:24px; padding:30px;
    box-shadow:0 0 45px rgba(0,234,255,.08), 0 25px 80px rgba(0,0,0,.55);
}
.login-title { text-align:center; font-size:34px; font-weight:900; color:#f3fbff; }
.login-subtitle { text-align:center; color:#7fa8bd; letter-spacing:1px; margin-bottom:22px; }
.login-dark-card label { color:#b8d7e8 !important; }
.login-dark-card input { background:#061525 !important; color:#f5fbff !important; border-color:#1c5270 !important; }
.login-dark-card input::placeholder { color:#5e8196 !important; }
.login-divider { display:flex; align-items:center; gap:10px; margin:16px 0; color:#62849a; font-size:13px; }
.login-divider::before,.login-divider::after { content:""; flex:1; height:1px; background:rgba(0,234,255,.18); }

/* HOME HERO */
.home-image img { border-radius:20px; border:1px solid rgba(0,234,255,.35); box-shadow:0 0 35px rgba(0,234,255,.13); }
[data-testid="stImage"] img { border-radius:18px; }

/* CODE / MISC */
.stMarkdown, .stCaption { color:#b2cfde; }
#MainMenu, footer { visibility:hidden; }
header[data-testid="stHeader"] { background:rgba(0,0,0,0); }
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATABASE
# =========================================================

create_tables()


# =========================================================
# LOAD ML MODEL
# =========================================================

model = joblib.load("phishing_model.pkl")


# =========================================================
# PASSWORD HASHING
# =========================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# =========================================================
# REGISTER USER
# =========================================================

def register_user(username, password):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        hashed_password = hash_password(password)

        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                password,
                role
            )
            VALUES
            (%s, %s, %s)
            """,
            (
                username,
                hashed_password,
                "user"
            )
        )

        connection.commit()

        return True

    except Exception:

        return False

    finally:

        cursor.close()
        connection.close()


# =========================================================
# LOGIN USER
# =========================================================

def login_user(username, password):

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    hashed_password = hash_password(password)

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username = %s
        AND password = %s
        """,
        (
            username,
            hashed_password
        )
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user


# =========================================================
# BASIC ML FEATURES
# =========================================================

def extract_features(url):

    parsed_url = urlparse(url)

    return [[

        len(url),

        url.count("."),

        url.count("/"),

        url.count("-"),

        sum(
            char.isdigit()
            for char in url
        ),

        url.count("@"),

        1 if parsed_url.scheme == "https" else 0

    ]]


# =========================================================
# CHECK IP ADDRESS
# =========================================================

def is_ip_address(hostname):

    if not hostname:
        return False

    try:

        ipaddress.ip_address(hostname)

        return True

    except ValueError:

        return False


# =========================================================
# ADVANCED URL ANALYSIS
# =========================================================

def advanced_url_analysis(url, prediction):

    original_url = url.strip()

    # Add scheme only for parsing
    if "://" not in original_url:

        parse_url = "http://" + original_url

    else:

        parse_url = original_url

    parsed_url = urlparse(parse_url)

    hostname = parsed_url.hostname or ""

    scheme = parsed_url.scheme.lower()

    # -----------------------------
    # Basic URL information
    # -----------------------------

    url_length = len(original_url)

    dot_count = original_url.count(".")

    hyphen_count = original_url.count("-")

    digit_count = sum(
        char.isdigit()
        for char in original_url
    )

    at_symbol = "@" in original_url

    https = scheme == "https"

    ip_address = is_ip_address(hostname)

    # -----------------------------
    # Suspicious keywords
    # -----------------------------

    suspicious_keywords = [

        "login",
        "signin",
        "sign-in",
        "verify",
        "verification",
        "secure",
        "security",
        "update",
        "account",
        "password",
        "bank",
        "wallet",
        "confirm",
        "confirmation",
        "free",
        "gift",
        "bonus",
        "winner",
        "win",
        "urgent",
        "unlock",
        "paypal",
        "credential"

    ]

    lower_url = original_url.lower()

    found_keywords = []

    for keyword in suspicious_keywords:

        if keyword in lower_url:

            found_keywords.append(keyword)

    suspicious_words = len(found_keywords) > 0

    # -----------------------------
    # Punycode
    # -----------------------------

    punycode = "xn--" in lower_url

    # -----------------------------
    # Port check
    # -----------------------------

    has_port = False

    try:

        if parsed_url.port is not None:

            has_port = True

    except ValueError:

        has_port = True

    # -----------------------------
    # Double slash in path
    # -----------------------------

    double_slash_path = (
        "//" in parsed_url.path
    )

    # -----------------------------
    # Hostname length
    # -----------------------------

    hostname_length = len(hostname)

    # =====================================================
    # RISK SCORE
    # =====================================================

    risk_score = 0

    reasons = []

    # HTTPS
    if not https:

        risk_score += 10

        reasons.append(
            "URL does not use HTTPS"
        )

    # IP address
    if ip_address:

        risk_score += 25

        reasons.append(
            "URL uses an IP address instead of a domain"
        )

    # @ symbol
    if at_symbol:

        risk_score += 20

        reasons.append(
            "URL contains @ symbol"
        )

    # URL length
    if url_length > 120:

        risk_score += 20

        reasons.append(
            "URL is very long"
        )

    elif url_length > 75:

        risk_score += 10

        reasons.append(
            "URL is longer than normal"
        )

    # dots
    if dot_count > 5:

        risk_score += 10

        reasons.append(
            "URL contains many dots"
        )

    elif dot_count > 3:

        risk_score += 5

        reasons.append(
            "URL contains multiple subdomains"
        )

    # hyphens
    if hyphen_count > 4:

        risk_score += 10

        reasons.append(
            "URL contains many hyphens"
        )

    elif hyphen_count > 2:

        risk_score += 5

        reasons.append(
            "URL contains multiple hyphens"
        )

    # digits
    if digit_count > 8:

        risk_score += 10

        reasons.append(
            "URL contains many numbers"
        )

    elif digit_count > 4:

        risk_score += 5

        reasons.append(
            "URL contains several numbers"
        )

    # suspicious keywords
    if suspicious_words:

        risk_score += 15

        reasons.append(
            "Suspicious security-related words detected"
        )

    # Punycode
    if punycode:

        risk_score += 15

        reasons.append(
            "Punycode domain detected"
        )

    # Port
    if has_port:

        risk_score += 10

        reasons.append(
            "Custom network port detected"
        )

    # Double slash
    if double_slash_path:

        risk_score += 10

        reasons.append(
            "Double slash found in URL path"
        )

    # Hostname length
    if hostname_length > 40:

        risk_score += 5

        reasons.append(
            "Hostname is unusually long"
        )

    # =====================================================
    # ML MODEL INFLUENCE
    # =====================================================

    if prediction == 1:

        # If ML detects phishing,
        # keep the score at least 75.

        risk_score = max(
            risk_score,
            75
        )

        reasons.append(
            "Machine learning model detected phishing characteristics"
        )

    # Keep score between 0 and 100
    risk_score = min(
        max(risk_score, 0),
        100
    )

    # =====================================================
    # THREAT LEVEL
    # =====================================================

    if risk_score >= 60:

        threat_level = "HIGH"

    elif risk_score >= 30:

        threat_level = "MEDIUM"

    else:

        threat_level = "LOW"

    # =====================================================
    # FINAL RESULT
    # =====================================================

    if prediction == 1:

        final_result = "Phishing"

    else:

        final_result = "Legitimate"

    # If no reasons
    if not reasons:

        reasons.append(
            "No major suspicious characteristics detected"
        )

    return {

        "url": original_url,

        "https": https,

        "ip_address": ip_address,

        "at_symbol": at_symbol,

        "suspicious_words": suspicious_words,

        "found_keywords": found_keywords,

        "url_length": url_length,

        "dot_count": dot_count,

        "hyphen_count": hyphen_count,

        "digit_count": digit_count,

        "punycode": punycode,

        "has_port": has_port,

        "double_slash_path": double_slash_path,

        "hostname": hostname,

        "hostname_length": hostname_length,

        "risk_score": risk_score,

        "threat_level": threat_level,

        "final_result": final_result,

        "reasons": reasons

    }


# =========================================================
# SAVE REPORT
# =========================================================

def save_report(
    url,
    result,
    risk_score,
    username
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO url_reports
        (
            url,
            result,
            risk_score,
            reported_by
        )
        VALUES
        (%s, %s, %s, %s)
        """,
        (
            url,
            result,
            risk_score,
            username
        )
    )

    connection.commit()

    cursor.close()
    connection.close()


# =========================================================
# GET USER REPORTS
# =========================================================

def get_reports(username):

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            id,
            url,
            result,
            risk_score,
            reported_by,
            created_at
        FROM url_reports
        WHERE reported_by = %s
        ORDER BY created_at DESC
        """,
        (username,)
    )

    reports = cursor.fetchall()

    cursor.close()
    connection.close()

    return reports


# =========================================================
# GET ALL USERS
# =========================================================

def get_all_users():

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            id,
            username,
            role
        FROM users
        ORDER BY id DESC
        """
    )

    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return users


# =========================================================
# GET ALL REPORTS
# =========================================================

def get_all_reports():

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            id,
            url,
            result,
            risk_score,
            reported_by,
            created_at
        FROM url_reports
        ORDER BY created_at DESC
        """
    )

    reports = cursor.fetchall()

    cursor.close()
    connection.close()

    return reports


# =========================================================
# ADMIN STATISTICS
# =========================================================

def get_admin_statistics():

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT COUNT(*) AS total_users
        FROM users
        """
    )

    total_users = cursor.fetchone()[
        "total_users"
    ]

    cursor.execute(
        """
        SELECT COUNT(*) AS total_reports
        FROM url_reports
        """
    )

    total_reports = cursor.fetchone()[
        "total_reports"
    ]

    cursor.execute(
        """
        SELECT COUNT(*) AS phishing_reports
        FROM url_reports
        WHERE result = 'Phishing'
        """
    )

    phishing_reports = cursor.fetchone()[
        "phishing_reports"
    ]

    cursor.execute(
        """
        SELECT COUNT(*) AS legitimate_reports
        FROM url_reports
        WHERE result = 'Legitimate'
        """
    )

    legitimate_reports = cursor.fetchone()[
        "legitimate_reports"
    ]

    cursor.close()
    connection.close()

    return (
        total_users,
        total_reports,
        phishing_reports,
        legitimate_reports
    )


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False


if "username" not in st.session_state:

    st.session_state.username = ""


if "role" not in st.session_state:

    st.session_state.role = "user"


if "auth_page" not in st.session_state:

    st.session_state.auth_page = "login"


if "last_url" not in st.session_state:

    st.session_state.last_url = ""


if "last_result" not in st.session_state:

    st.session_state.last_result = ""


if "last_risk" not in st.session_state:

    st.session_state.last_risk = 0


if "reported" not in st.session_state:

    st.session_state.reported = False


if "last_analysis" not in st.session_state:

    st.session_state.last_analysis = None


# =========================================================
# GOOGLE / APPLE LOGIN SESSION
# =========================================================

def handle_social_login():

    try:

        if hasattr(st, "user") and st.user.is_logged_in:

            user_name = st.user.get("name")

            if not user_name:
                user_name = st.user.get("email")

            if not user_name:
                user_name = "Social User"

            st.session_state.logged_in = True
            st.session_state.username = user_name
            st.session_state.role = "user"

            return True

    except Exception:

        pass

    return False


handle_social_login()


# =========================================================
# LOGIN / REGISTER PAGE
# =========================================================

if not st.session_state.logged_in:

    left, center, right = st.columns(
        [1, 0.7, 1]
    )

    with center:

        st.markdown(
            '<div class="login-dark-card">',
            unsafe_allow_html=True
        )

        # Login image only: assets/login_image.png
        if os.path.exists("assets/login_image.png"):

            st.image(
                "assets/login_image.png",
                width=260
            )

        st.markdown(
            '<div class="login-title">'
            '🛡️ PhishGuard'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="login-subtitle">'
            'Cybersecurity URL Detection System'
            '</div>',
            unsafe_allow_html=True
        )

        # =================================================
        # LOGIN
        # =================================================

        if st.session_state.auth_page == "login":

            st.subheader("🔐 Login")

            username = st.text_input(
                "Username",
                placeholder="Enter your username"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password"
            )

            if st.button(
                "🔐 Login",
                use_container_width=True
            ):

                if not username or not password:

                    st.warning(
                        "Please enter username and password."
                    )

                else:

                    user = login_user(
                        username,
                        password
                    )

                    if user:

                        st.session_state.logged_in = True

                        st.session_state.username = (
                            user["username"]
                        )

                        st.session_state.role = (
                            user["role"]
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Invalid username or password."
                        )

            st.markdown(
                '<div class="login-divider">or continue with</div>',
                unsafe_allow_html=True
            )

            if st.button(
                "🌐  Continue with Google",
                use_container_width=True,
                key="google_login"
            ):

                st.login("google")

            if st.button(
                "  Continue with Apple",
                use_container_width=True,
                key="apple_login"
            ):

                st.login("apple")

            st.write("")

            if st.button(
                "📝 Create New Account",
                use_container_width=True
            ):

                st.session_state.auth_page = (
                    "register"
                )

                st.rerun()

        # =================================================
        # REGISTER
        # =================================================

        else:

            st.subheader(
                "📝 Create Account"
            )

            username = st.text_input(
                "Create Username",
                placeholder="Enter username"
            )

            password = st.text_input(
                "Create Password",
                type="password",
                placeholder="Minimum 6 characters"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter password"
            )

            if st.button(
                "📝 Create Account",
                use_container_width=True
            ):

                if not username or not password:

                    st.warning(
                        "Please fill all fields."
                    )

                elif password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                elif len(password) < 6:

                    st.warning(
                        "Password must contain at least 6 characters."
                    )

                elif register_user(
                    username,
                    password
                ):

                    st.success(
                        "Account created successfully!"
                    )

                    st.session_state.auth_page = (
                        "login"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Username already exists."
                    )

            st.write("")

            if st.button(
                "⬅️ Back to Login",
                use_container_width=True
            ):

                st.session_state.auth_page = (
                    "login"
                )

                st.rerun()

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# =========================================================
# MAIN APPLICATION
# =========================================================

else:

    # =====================================================
    # SIDEBAR
    # =====================================================

    with st.sidebar:

        st.markdown(
            '<div class="sidebar-title">'
            '🛡️ PhishGuard'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="sidebar-subtitle">'
            'Cybersecurity Protection'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")

        st.write(
            f"👤 **{st.session_state.username}**"
        )

        if st.session_state.role == "admin":

            st.success(
                "🔐 Administrator"
            )

        st.markdown("---")

        navigation = [

            "🏠 Home",

            "🔍 URL Scanner",

            "📋 My Reports"

        ]

        if st.session_state.role == "admin":

            navigation.append(
                "📊 Admin Dashboard"
            )

        page = st.radio(
            "Navigation",
            navigation
        )

        st.markdown("---")

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False

            st.session_state.username = ""

            st.session_state.role = "user"

            st.session_state.last_url = ""

            st.session_state.last_result = ""

            st.session_state.last_risk = 0

            st.session_state.last_analysis = None

            st.session_state.reported = False

            st.rerun()


    # =====================================================
    # HOME
    # =====================================================

    if page == "🏠 Home":

        st.markdown(
            '<div class="main-title">'
            '🛡️ PhishGuard'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="main-subtitle">'
            'Cybersecurity URL Detection & Reporting System'
            '</div>',
            unsafe_allow_html=True
        )

        # -------------------------------------------------
        # HOME IMAGE
        # -------------------------------------------------

        if os.path.exists(
            "home_banner.png"
        ):

            image_left, image_center, image_right = (
                st.columns([1, 2, 1])
            )

            with image_center:

                st.image(
                    "home_banner.png",
                    width=450
                )

        st.markdown("---")

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            'Welcome to PhishGuard 🛡️'
            '</div>',
            unsafe_allow_html=True
        )

        st.write(
            """
            PhishGuard is a cybersecurity system that
            analyzes website URLs and detects suspicious
            phishing characteristics using machine learning
            and URL security analysis.
            """
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        st.subheader(
            "🔐 Security Features"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown(
                '<div class="card">',
                unsafe_allow_html=True
            )

            st.subheader(
                "🔍 URL Scanner"
            )

            st.write(
                "Analyze website URLs using the ML model and advanced security checks."
            )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                '<div class="card">',
                unsafe_allow_html=True
            )

            st.subheader(
                "🚨 URL Reporting"
            )

            st.write(
                "Report suspicious URLs to the security database."
            )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

        with col3:

            st.markdown(
                '<div class="card">',
                unsafe_allow_html=True
            )

            st.subheader(
                "🛡️ Risk Analysis"
            )

            st.write(
                "View URL risk score and threat level."
            )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


    # =====================================================
    # URL SCANNER
    # =====================================================

    elif page == "🔍 URL Scanner":

        st.markdown(
            '<div class="section-title">'
            '🔍 Advanced Phishing URL Scanner'
            '</div>',
            unsafe_allow_html=True
        )

        st.write(
            "Enter a website URL for detailed security analysis."
        )

        url = st.text_input(
            "🌐 Website URL",
            placeholder="https://example.com"
        )

        if st.button(
            "🔍 Analyze URL",
            use_container_width=True
        ):

            if not url.strip():

                st.warning(
                    "Please enter a website URL."
                )

            else:

                clean_url = url.strip()

                # -----------------------------------------
                # ML MODEL
                # -----------------------------------------

                features = extract_features(
                    clean_url
                )

                prediction = model.predict(
                    features
                )[0]

                # -----------------------------------------
                # ADVANCED ANALYSIS
                # -----------------------------------------

                analysis = advanced_url_analysis(
                    clean_url,
                    prediction
                )

                # -----------------------------------------
                # SAVE SESSION
                # -----------------------------------------

                st.session_state.last_url = (
                    clean_url
                )

                st.session_state.last_result = (
                    analysis["final_result"]
                )

                st.session_state.last_risk = (
                    analysis["risk_score"]
                )

                st.session_state.last_analysis = (
                    analysis
                )

                st.session_state.reported = False


        # =================================================
        # DISPLAY LAST ANALYSIS
        # =================================================

        if st.session_state.last_analysis:

            analysis = (
                st.session_state.last_analysis
            )

            st.markdown("---")

            st.subheader(
                "🔍 URL Analysis"
            )

            st.markdown(
                '<div class="analysis-card">',
                unsafe_allow_html=True
            )

            st.write(
                f"🌐 **URL:** `{analysis['url']}`"
            )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


            # =================================================
            # SECURITY CHECKS
            # =================================================

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                if analysis["https"]:

                    st.success(
                        "🔒 HTTPS\n\nEnabled"
                    )

                else:

                    st.warning(
                        "🔓 HTTPS\n\nNot Used"
                    )

            with col2:

                if analysis["ip_address"]:

                    st.error(
                        "🌐 IP Address\n\nDetected"
                    )

                else:

                    st.success(
                        "🌐 IP Address\n\nNot Detected"
                    )

            with col3:

                if analysis["at_symbol"]:

                    st.error(
                        "⚠️ @ Symbol\n\nDetected"
                    )

                else:

                    st.success(
                        "⚠️ @ Symbol\n\nNot Detected"
                    )

            with col4:

                if analysis["suspicious_words"]:

                    st.warning(
                        "🔑 Keywords\n\nDetected"
                    )

                else:

                    st.success(
                        "🔑 Keywords\n\nNone"
                    )


            # =================================================
            # URL FEATURES
            # =================================================

            st.markdown("---")

            st.subheader(
                "📊 URL Features"
            )

            feature1, feature2, feature3 = st.columns(3)

            with feature1:

                st.metric(
                    "URL Length",
                    analysis["url_length"]
                )

                st.metric(
                    "Dots",
                    analysis["dot_count"]
                )

                st.metric(
                    "Hyphens",
                    analysis["hyphen_count"]
                )

            with feature2:

                st.metric(
                    "Digits",
                    analysis["digit_count"]
                )

                st.metric(
                    "Hostname Length",
                    analysis["hostname_length"]
                )

                st.metric(
                    "Suspicious Words",
                    len(
                        analysis["found_keywords"]
                    )
                )

            with feature3:

                if analysis["punycode"]:

                    st.error(
                        "Punycode: Detected"
                    )

                else:

                    st.success(
                        "Punycode: Not Detected"
                    )

                if analysis["has_port"]:

                    st.warning(
                        "Custom Port: Detected"
                    )

                else:

                    st.success(
                        "Custom Port: Not Detected"
                    )

                if analysis["double_slash_path"]:

                    st.warning(
                        "Double Slash: Detected"
                    )

                else:

                    st.success(
                        "Double Slash: Not Detected"
                    )


            # =================================================
            # RISK SCORE
            # =================================================

            st.markdown("---")

            st.subheader(
                "🛡️ Security Risk Assessment"
            )

            risk_col1, risk_col2 = st.columns(2)

            with risk_col1:

                st.metric(
                    "🛡️ Risk Score",
                    f"{analysis['risk_score']}/100"
                )

            with risk_col2:

                if analysis["threat_level"] == "HIGH":

                    st.error(
                        "🔴 Threat Level: HIGH"
                    )

                elif analysis["threat_level"] == "MEDIUM":

                    st.warning(
                        "🟠 Threat Level: MEDIUM"
                    )

                else:

                    st.success(
                        "🟢 Threat Level: LOW"
                    )


            # =================================================
            # FINAL RESULT
            # =================================================

            st.markdown("---")

            if analysis["final_result"] == "Phishing":

                st.error(
                    "🚨 Phishing URL Detected!"
                )

                st.write(
                    "The machine learning model detected phishing characteristics in this URL."
                )

            else:

                st.success(
                    "✅ Legitimate URL"
                )

                st.write(
                    "The machine learning model did not classify this URL as phishing."
                )


            # =================================================
            # SUSPICIOUS REASONS
            # =================================================

            st.markdown("---")

            st.subheader(
                "⚠️ Security Analysis"
            )

            if analysis["found_keywords"]:

                st.write(
                    "🔑 **Suspicious keywords:** "
                    + ", ".join(
                        analysis["found_keywords"]
                    )
                )

            st.markdown(
                '<div class="analysis-card">',
                unsafe_allow_html=True
            )

            for reason in analysis["reasons"]:

                st.write(
                    f"• {reason}"
                )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


            # =================================================
            # REPORT PHISHING URL
            # =================================================

            if (
                analysis["final_result"]
                == "Phishing"
            ):

                st.markdown("---")

                st.subheader(
                    "🚨 Report Suspicious URL"
                )

                st.write(
                    "Report this URL to the PhishGuard security database."
                )

                if not st.session_state.reported:

                    if st.button(
                        "🚨 Report URL",
                        use_container_width=True
                    ):

                        save_report(
                            analysis["url"],
                            analysis["final_result"],
                            analysis["risk_score"],
                            st.session_state.username
                        )

                        st.session_state.reported = True

                        st.success(
                            "✅ URL reported successfully!"
                        )

                        st.rerun()

                else:

                    st.success(
                        "✅ This URL has already been reported."
                    )


    # =====================================================
    # MY REPORTS
    # =====================================================

    elif page == "📋 My Reports":

        st.markdown(
            '<div class="section-title">'
            '📋 My Reports'
            '</div>',
            unsafe_allow_html=True
        )

        reports = get_reports(
            st.session_state.username
        )

        st.metric(
            "📊 Total Reports",
            len(reports)
        )

        if reports:

            for report in reports:

                st.markdown(
                    '<div class="report-card">',
                    unsafe_allow_html=True
                )

                st.write(
                    f"🆔 **Report ID:** "
                    f"{report['id']}"
                )

                st.write(
                    f"🌐 **URL:** "
                    f"{report['url']}"
                )

                st.write(
                    f"⚠️ **Result:** "
                    f"{report['result']}"
                )

                st.write(
                    f"🛡️ **Risk Score:** "
                    f"{report['risk_score']}/100"
                )

                st.write(
                    f"🕒 **Date:** "
                    f"{report['created_at']}"
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

        else:

            st.info(
                "📭 You have not reported any URLs yet."
            )


    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    elif page == "📊 Admin Dashboard":

        st.markdown(
            '<div class="section-title">'
            '📊 Admin Dashboard'
            '</div>',
            unsafe_allow_html=True
        )

        st.write(
            "Monitor users, reports and URL security activity."
        )

        (
            total_users,
            total_reports,
            phishing_reports,
            legitimate_reports
        ) = get_admin_statistics()


        # =================================================
        # ADMIN METRICS
        # =================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "👥 USERS",
                total_users
            )

        with col2:

            st.metric(
                "📋 REPORTS",
                total_reports
            )

        with col3:

            st.metric(
                "🚨 PHISHING",
                phishing_reports
            )

        with col4:

            st.metric(
                "✅ LEGITIMATE",
                legitimate_reports
            )


        st.markdown("---")


        # =================================================
        # ALL REPORTS
        # =================================================

        st.subheader(
            "🚨 All Reported URLs"
        )

        all_reports = get_all_reports()

        if all_reports:

            for report in all_reports:

                st.markdown(
                    '<div class="report-card">',
                    unsafe_allow_html=True
                )

                st.write(
                    f"🆔 **Report ID:** "
                    f"{report['id']}"
                )

                st.write(
                    f"🌐 **URL:** "
                    f"{report['url']}"
                )

                st.write(
                    f"⚠️ **Result:** "
                    f"{report['result']}"
                )

                st.write(
                    f"🛡️ **Risk Score:** "
                    f"{report['risk_score']}/100"
                )

                st.write(
                    f"👤 **Reported By:** "
                    f"{report['reported_by']}"
                )

                st.write(
                    f"🕒 **Date:** "
                    f"{report['created_at']}"
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

        else:

            st.info(
                "📭 No reports available."
            )


        st.markdown("---")


        # =================================================
        # REGISTERED USERS
        # =================================================

        st.subheader(
            "👥 Registered Users"
        )

        users = get_all_users()

        if users:

            for user in users:

                st.write(
                    f"🆔 {user['id']}  |  "
                    f"👤 {user['username']}  |  "
                    f"🔐 {user['role']}"
                )

        else:

            st.info(
                "No users found."
            )
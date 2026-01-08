import streamlit as st
import base64
from groq import Groq
from PyPDF2 import PdfReader
import urllib.parse

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Masood Alam Eye Diagnostics",
    layout="wide",
    page_icon="👁️"
)

# =========================================================
# STYLING (CSS)
# =========================================================
st.markdown("""
<style>
/* 1. MAIN BACKGROUND COLOR (Off-White) */
.stApp {
    background-color: #fafafa; /* Soft off-white color */
}

/* 2. CONTAINER PADDING */
.block-container {
    padding: 1rem;
    max-width: 100%;
}

/* 3. HIDE STREAMLIT ELEMENTS */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* 4. CUSTOM TITLE STYLE */
.report-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #0e1117;
    border-bottom: 3px solid #ff4b4b;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
}

/* 5. GREEN REPORT STYLE (Matches Image 2a) */
/* This targets the st.code box to make it green */
[data-testid="stCodeBlock"] {
    background-color: #dcfce7 !important; /* Light Green Background */
    border: 1px solid #86efac;            /* Slightly darker green border */
    border-radius: 10px;
    padding: 15px;
}
/* Ensures text inside the green box is dark and readable */
[data-testid="stCodeBlock"] code {
    color: #064e3b !important;            /* Dark Green/Black text */
    font-family: sans-serif !important;   /* Cleaner look than monospace */
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# API KEY
# =========================================================
try:
    api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("GROQ_API_KEY not found in Streamlit secrets.")
    st.stop()

client = Groq(api_key=api_key)

# =========================================================
# HEADER & SHARE APP BUTTON (Top Right)
# =========================================================
col_header, col_share = st.columns([7, 2])

with col_header:
    st.title("👁️ Masood Alam Eye Diagnostics")
    st.markdown("**AI-Powered Ophthalmic Consultant**")

with col_share:
    # WhatsApp Encoding for App Link Only
    app_url = "https://eye-diagnostics.streamlit.app/"
    encoded_app_url = urllib.parse.quote(f"Check out this AI Eye Diagnostic tool: {app_url}")
    st.write("") 
    st.link_button("📤 Share App", f"https://wa.me/?text={encoded_app_url}")

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("Imaging Modality")

    modality = st.radio(
        "Select modality",
        [
            "OCT Macula",
            "OCT ONH (Glaucoma)",
            "Visual Field (Perimetry)",
            "Corneal Topography",
            "Fluorescein Angiography (FFA)",
            "OCT Angiography (OCTA)",
            "Ultrasound B-Scan"
        ]
    )

    report_style = st.selectbox(
        "Reporting style",
        ["Consultant Clinical Report", "Exam-Oriented (FCPS / MRCOphth)"]
    )

    st.divider()
    st.info(
        "**Instructions:**\n"
        "1. Select the correct modality.\n"
        "2. Tap 'Browse files'.\n"
        "3. Select an image from your device."
    )

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def encode_image(file):
    return base64.b64encode(file.getvalue()).decode("utf-8")

def load_reference_text(path="REFERNCE.pdf"):
    try:
        reader = PdfReader(path)
        text = ""
        for i, page in enumerate(reader.pages):
            if i >

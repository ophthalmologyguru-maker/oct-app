import streamlit as st
import base64
from groq import Groq
from PyPDF2 import PdfReader

# =========================================================
# PAGE CONFIGURATION (NEUTRAL BRANDING)
# =========================================================
st.set_page_config(
    page_title="AI Ophthalmic Imaging Support",
    layout="wide",
    page_icon="👁️"
)

# =========================================================
# STYLING (NEUTRAL, NON-BRANDED)
# =========================================================
st.markdown("""
<style>
.block-container {
    padding: 1rem;
    max-width: 100%;
}
div[data-testid="stCameraInput"] video {
    width: 100% !important;
    object-fit: cover;
    border-radius: 8px;
}
.report-title {
    font-size: 1.2rem;
    font-weight: 600;
    border-bottom: 2px solid #cccccc;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# API KEY
# =========================================================
try:
    api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("API key not configured.")
    st.stop()

client = Groq(api_key=api_key)

# =========================================================
# HEADER (GENERIC, SAFE)
# =========================================================
st.title("👁️ AI Ophthalmic Imaging Support")
st.caption("AI-assisted clinical interpretation support for eye-care professionals")

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("Imaging Modality")

    modality = st.radio(
        "Select modality",
        [
            "OCT Macula",
            "OCT Optic Nerve Head",
            "Visual Field (Perimetry)",
            "Corneal Topography",
            "Fluorescein Angiography",
            "OCT Angiography",
            "Ultrasound B-Scan"
        ]
    )

    input_method = st.radio(
        "Input method",
        ["Upload Image", "Use Camera"]
    )

    report_style = st.selectbox(
        "Report style",
        ["Clinical Support Report", "Exam-Oriented Summary"]
    )

    # -----------------------------------------------------
    # PERMANENT DISCLAIMER (SIDEBAR)
    # -----------------------------------------------------
    st.divider()
    st.warning(
        "⚠️ **AI Medical Disclaimer**\n\n"
        "This application uses artificial intelligence to assist with the interpretation "
        "of ophthalmic imaging.\n\n"
        "The output is provided for educational and clinical support purposes only and "
        "does **not** constitute a medical dia

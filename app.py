import streamlit as st
import base64
from groq import Groq
from PyPDF2 import PdfReader

# =========================================================
# PAGE CONFIGURATION (NEUTRAL, NON-BRANDED)
# =========================================================
st.set_page_config(
    page_title="AI Ophthalmic Imaging Support",
    layout="wide",
    page_icon="👁️"
)

# =========================================================
# STYLING
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

# ==================================================

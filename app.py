import streamlit as st
import base64
from groq import Groq
from PyPDF2 import PdfReader

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Masood Alam Eye Diagnostics",
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
/* Hides the 'deploy' button and hamburger menu for cleaner look */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.report-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #0e1117;
    border-bottom: 3px solid #ff4b4b;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
}
/* Highlighting the disclaimer to ensure visibility */
.stAlert {
    font-weight: 600;
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
# HEADER
# =========================================================
st.title("👁️ Masood Alam Eye Diagnostics")
st.markdown("**AI-Powered Ophthalmic Consultant**")

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    # --- PROMINENT DISCLAIMER ---
    st.warning(
        """
        ⚠️ **AI MEDICAL DISCLAIMER**
        
        This application uses artificial intelligence to assist in the interpretation of ophthalmic images.
        
        The output is for **educational and clinical support purposes only** and **does not constitute a medical diagnosis, clinical decision, or treatment recommendation.**
        
        All results must be interpreted by a **qualified ophthalmologist** in conjunction with clinical examination, patient history, and other relevant investigations.
        
        **This tool does not replace professional medical judgment.**
        """
    )
    
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
        "1. Acknowledge the disclaimer below.\n"
        "2. Select the correct modality.\n"
        "3. Tap 'Browse files' to upload."
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
            if i > 50: break
            text += page.extract_text() or ""
        return text[:5000]
    except:
        return ""

# =========================================================
# SYSTEM PROMPT
# =========================================================
SYSTEM_PROMPT = """
You are an expert Consultant Ophthalmologist (Dr. Masood Alam Shah).
Your task is to analyze the provided ophthalmic scan and generate a formal clinical report.

STRICT FORMATTING RULES:
1. **HEADLINES MUST BE BOLD AND UPPERCASE** (e.g., **SCAN QUALITY:**).
2. **EXTRACT PATIENT DATA**: You MUST look for Patient Name, ID, DOB, and Age in the image. If found, list them at the top.
3. **NO FLUFF**: Do not use phrases like "Step 1" or "The image shows". Start directly with the findings.
4. **PROFESSIONAL TONE**: Use precise medical terminology.

REQUIRED OUTPUT STRUCTURE:

**PATIENT DATA:**
- Name: [Extract or "Not Visible"]
- ID: [Extract or "Not Visible"]
- Age/DOB: [Extract or "Not Visible"]
- Date of Scan: [Extract or "Not Visible"]

**SCAN QUALITY:**
(Assess signal strength, centration, and artifacts)

**KEY FINDINGS:**
(Bulleted list of specific anatomical and pathological findings)

**QUANTITATIVE ANALYSIS:**
(Extract specific numbers if visible: e.g., RNFL thickness, CSM

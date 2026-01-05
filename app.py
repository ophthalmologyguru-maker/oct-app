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
        "1. Select modality.\n"
        "2. Upload scan.\n"
        "3. Acknowledge disclaimer.\n"
        "4. Click Analyze."
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
(Extract specific numbers if visible: e.g., RNFL thickness, CSMT, C/D Ratio, MD, PSD)

**CLINICAL IMPRESSION:**
(A concise, probability-based diagnostic summary)

**MANAGEMENT SUGGESTIONS:**
(Brief recommendations for follow-up or further testing)
"""

MODALITY_INSTRUCTIONS = {
    "OCT Macula": "Focus on: CSMT, Retinal Layers (ILM, ELM, IS/OS), Fluid (IRF/SRF), and RPE status.",
    "OCT ONH (Glaucoma)": "Focus on: RNFL Thickness (Average & Quadrants), Cup-to-Disc Ratio, and ISNT rule.",
    "Visual Field (Perimetry)": "Focus on: Reliability indices, GHT, Mean Deviation (MD), PSD, and defect patterns (Arcuate/Nasal Step).",
    "Corneal Topography": "Focus on: K-max, Thinnest Pachymetry, and Anterior/Posterior Elevation maps.",
    "Fluorescein Angiography (FFA)": "Focus on: Phases (Arterial/Venous), Leakage vs Staining vs Pooling, and Ischemia.",
    "OCT Angiography (OCTA)": "Focus on: Vascular density, FAZ size, and Neovascular networks.",
    "Ultrasound B-Scan": "Focus on: Retinal attachment, Vitreous echoes (Hemorrhage), and Mass lesions."
}

# =========================================================
# MAIN APP LOGIC
# =========================================================
st.write(f"### Upload {modality} Scan")

st.info("ℹ️ **Note:** Tap **'Browse files'** to upload an image from your **Device** (Android, iPhone, PC, Mac, or Linux).") 

image_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

st.warning(
    """
    ⚠️ **AI MEDICAL DISCLAIMER**
    
    This application uses artificial intelligence to assist in the interpretation of ophthalmic images.
    The output is for **educational and clinical support purposes only** and **does not constitute a medical diagnosis.**
    **This tool does not replace professional medical judgment.**
    """
)

acknowledgement = st.checkbox(
    "✅ I acknowledge that I have read the disclaimer above and understand this tool is for support purposes only."
)

if image_file:
    # Show Preview
    st.image(image_file, caption="Scan Preview", width=300)
    
    if acknowledgement:
        if st.button("Analyze Scan", type="primary"):
            with st.spinner("Dr. Masood's AI is analyzing..."):
                try:
                    encoded_image = encode_image(image_file)
                    reference_text = load_reference_text()

                    user_prompt = f"""
                    MODALITY: {modality}
                    CONTEXT: {MODALITY_INSTRUCTIONS[modality]}
                    REFERENCE DATA: {reference_text}
                    """

                    messages = [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{encoded_image}"
                                    }
                                }
                            ]
                        }
                    ]

                    response = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=messages,
                        temperature=0.1
                    )

                    st.markdown("<div class='report-title'>📋 Clinical Report</div>", unsafe_allow_html=True)
                    st.markdown(response.choices[0].message.content)
                    st.success("Analysis Complete")

                except Exception as e:
                    st.error(f"Analysis Error: {e}")
    else:
        st.info("👆 **Please check the acknowledgement box above to enable the Analyze button.**")

# =========================================================
# FOOTER
# =========================================================
st.markdown(
    "<hr><center><small>Masood Alam Eye Diagnostics | AI Clinical Support Tool</small></center>",
    unsafe_allow_html=True
)

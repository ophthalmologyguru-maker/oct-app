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
.report-title {
    font-size: 1.3rem;
    font-weight: 700;
    border-bottom: 2px solid #ff4b4b;
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
    st.error("GROQ_API_KEY not found in Streamlit secrets.")
    st.stop()

client = Groq(api_key=api_key)

# =========================================================
# HEADER
# =========================================================
st.title("👁️ Masood Alam Eye Diagnostics")
st.caption("AI-assisted ophthalmic imaging interpretation")

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

    # -----------------------------------------------------
    # SIDEBAR DISCLAIMER (ALWAYS VISIBLE)
    # -----------------------------------------------------
    st.divider()
    st.warning(
        "⚠️ **AI Medical Disclaimer**\n\n"
        "This application uses artificial intelligence to assist in the interpretation "
        "of ophthalmic imaging.\n\n"
        "The output is for educational and clinical support purposes only and does not "
        "constitute a medical diagnosis, treatment recommendation, or clinical decision.\n\n"
        "Final interpretation and patient management must be performed by a qualified ophthalmologist."
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
            if i > 40:
                break
            text += page.extract_text() or ""
        return text[:4000]
    except:
        return ""

# =========================================================
# SYSTEM PROMPT (REGULATORY + SAFETY GUARDRAIL)
# =========================================================
SYSTEM_PROMPT = """
You are an artificial intelligence system designed to assist qualified ophthalmologists
by generating structured ophthalmic imaging reports.

REGULATORY & SAFETY RULES (NON-NEGOTIABLE):
- You are NOT a diagnostic system
- You do NOT provide medical diagnoses or treatment recommendations
- You provide clinical support only
- All language must be probability-based and non-definitive
- Use phrases such as:
  "findings are consistent with"
  "features are suggestive of"
  "correlation with clinical findings is advised"

STRICTLY PROHIBITED:
- "diagnosis confirmed"
- "this proves"
- "definitive diagnosis"
- Any treatment advice
- Teaching or explanatory language

MANDATORY OUTPUT STRUCTURE (EXACTLY AS BELOW):

**PATIENT DETAILS:**
(Extract Name, ID, Age, DOB, and Date of Scan if visible. If not visible, state "Not visible in scan".)

**SCAN QUALITY:**
(Assess signal strength and centration)

**KEY FINDINGS:**
(List observations clearly)

**PATTERN ANALYSIS:**
(Analyze specific patterns relevant to the modality)

**CLINICAL IMPRESSION:**
(Probability-based summary)

**DIFFERENTIAL CONSIDERATIONS:**
(List 2-3 possibilities)

**LIMITATIONS / NOTES:**
(Standard limitations of AI analysis)
"""

# =========================================================
# MODALITY-SPECIFIC INSTRUCTIONS
# =========================================================
MODALITY_INSTRUCTIONS = {
    "OCT Macula": """
Focus on:
- Retinal thickness profile
- Intraretinal fluid (IRF) / subretinal fluid (SRF)
- Integrity of ELM and ellipsoid zone
- RPE changes (drusen, PED, atrophy)
""",

    "OCT ONH (Glaucoma)": """
Focus on:
- RNFL average and quadrant thickness
- ISNT rule assessment
- Optic disc morphology and cupping
""",

    "Visual Field (Perimetry)": """
Focus on:
- Reliability indices
- Mean deviation (MD), PSD, GHT
- Pattern: arcuate defect, nasal step, central island
""",

    "Corneal Topography": """
Focus on:
- Axial curvature pattern
- Anterior/posterior elevation
- Pachymetry and thinnest point
""",

    "Fluorescein Angiography (FFA)": """
Focus on:
- Angiographic phase
- Leakage, pooling, staining, window defects
- Areas of non-perfusion
""",

    "OCT Angiography (OCTA)": """
Focus on:
- Superficial and deep capillary plexus
- FAZ morphology
- Neovascular networks
""",

    "Ultrasound B-Scan": """
Focus on:
- Retinal vs vitreous detachment
- Mass reflectivity
- Dynamic movement
"""
}

# =========================================================
# IMAGE INPUT (FILE UPLOAD ONLY)
# =========================================================
st.write(f"### Upload {modality} Scan")
image_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

# =========================================================
# USER ACKNOWLEDGEMENT (HARD GATE)
# =========================================================
st.divider()
consent = st.checkbox(
    "I understand that this is an AI-assisted clinical support tool and does not replace professional medical judgment."
)

if image_file and not consent:
    st.warning("Please acknowledge the AI medical disclaimer to proceed.")

# =========================================================
# ANALYSIS
# =========================================================
if image_file and consent and st.button("Analyze Scan"):
    with st.spinner("Generating clinical report..."):
        try:
            encoded_image = encode_image(image_file)
            reference_text = load_reference_text()

            user_prompt = f"""
MODALITY: {modality}
REPORT STYLE: {report_style}

INSTRUCTIONS:
{MODALITY_INSTRUCTIONS[modality]}

REFERENCE TERMINOLOGY (FOR LANGUAGE CONSISTENCY ONLY):
{reference_text}
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
                temperature=0.2
            )

            # -------------------------------------------------
            # REPORT-LEVEL DISCLAIMER
            # -------------------------------------------------
            st.info(
                "⚠️ **AI-Generated Clinical Support Output** \n"
                "This report is generated by an artificial intelligence system and is intended "
                "to support clinical assessment only. It does not replace professional medical "
                "judgment. Correlation with clinical findings is essential."
            )

            st.markdown("<div class='report-title'>📋 Clinical Imaging Report</div>", unsafe_allow_html=True)
            st.markdown(response.choices[0].message.content)

            st.success("Report generated successfully")

        except Exception as e:
            st.error(f"Analysis failed: {e}")

# =========================================================
# FOOTER DISCLAIMER
# =========================================================
st.markdown(
    "<hr style='margin-top:2rem;'>"
    "<small style='color:gray;'>"
    "Masood Alam Eye Diagnostics is an AI-assisted clinical support tool. "
    "It does not provide medical diagnoses or treatment advice. "
    "Use is subject to professional clinical judgment."
    "</small>",
    unsafe_allow_html=True
)

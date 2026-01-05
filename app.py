import streamlit as st
import os
from groq import Groq
import base64
from PIL import Image
from PyPDF2 import PdfReader

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Masood Alam Eye Diagnostics", layout="wide", page_icon="👁️")

# --- CSS HACK FOR FULL-WIDTH CAMERA ---
st.markdown(
    """
    <style>
    div[data-testid="stCameraInput"] {
        width: 100% !important;
    }
    div[data-testid="stCameraInput"] video {
        width: 100% !important;
        height: auto !important;
        object-fit: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Access API Key
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Security Error: API Key not found in Secrets.")
    st.stop()

# --- HEADER ---
st.title("👁️ Masood Alam Eye Diagnostics")
st.markdown("### AI-Powered Ophthalmic Consultant")

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("Select Modality")
    task_type = st.radio(
        "Modality:",
        [
            "OCT (Retina)", 
            "Visual Field (Perimetry)", 
            "Corneal Topography", 
            "Fluorescein Angiography (FFA)", 
            "OCT Angiography (OCTA)",
            "Ultrasound B-Scan"
        ]
    )
    st.divider()
    input_method = st.radio("Input:", ["Upload Image File", "Use Camera"])
    st.info(f"Mode: **{task_type}**")

# --- 3. HELPER FUNCTIONS ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def get_pdf_text(filename="REFERNCE.pdf"):
    try:
        reader = PdfReader(filename)
        text = ""
        # Read first 50 pages to ensure all chapters are covered
        for i, page in enumerate(reader.pages):
            if i > 50: break 
            text += page.extract_text()
        return text
    except FileNotFoundError:
        return "Reference text not available. Relying on internal medical knowledge."

# --- 4. MAIN LOGIC ---
image_file = None

if input_method == "Upload Image File":
    image_file = st.file_uploader("Upload Scan", type=['png', 'jpg', 'jpeg'])
else:
    image_file = st.camera_input("Capture Scan")

if image_file and st.button("Analyze Scan"):
    with st.spinner("Consulting Dr. Masood's AI..."):
        try:
            client = Groq(api_key=api_key)
            base64_image = encode_image(image_file)
            book_text = get_pdf_text("REFERNCE.pdf")

            # --- PROFESSIONAL CLINICAL PROMPTS ---
            # These prompts force the AI to act like a doctor, not a teacher.
            
            if task_type == "OCT (Retina)":
                specific_instruction = """
                REPORT FORMAT:
                1. **Scan Quality**: Comment on Signal Strength (aim for >6) and Centration.
                2. **Morphology**: Describe retinal interface (vitreous), layers (ILM to RPE), and contour.
                3. **Pathology**: Identify Fluid (SRF/IRF), Edema (CSMT), Drusen, or Disruption.
                4. **Impression**: Give a concise diagnosis (e.g., 'Consistent with DME' or 'Wet AMD').
                """
            
            elif task_type == "Visual Field (Perimetry)":
                specific_instruction = """
                REPORT FORMAT:
                1. **Reliability**: Analyze Fixation Losses (<20%), False Pos/Neg (<33%). Check for 'Trigger Happy' (dB >40).
                2. **Pattern Deviation**: Describe defects (e.g., Arcuate, Nasal Step, Central Island, Altitudinal).
                3. **Indices**: Interpret GHT (Outside Normal Limits?), MD (severity), and PSD (focal loss).
                4. **Correlate**: Suggest if consistent with Glaucoma (horizontal raphe respect) or Neuro (vertical midline).
                """
            
            elif task_type == "Corneal Topography":
                specific_instruction = """
                REPORT FORMAT:
                1. **Curvature**: Analyze Axial Map (Steepening patterns, K-max).
                2. **Elevation**: Check Anterior/Posterior Float (Islands of elevation).
                3. **Pachymetry**: Locate thinnest point.
                4. **Impression**: Keratoconus vs. Regular Astigmatism vs. Normal.
                """
            
            elif task_type == "Fluorescein Angiography (FFA)":
                specific_instruction = """
                REPORT FORMAT:
                1. **Phase**: Identify arterial, arteriovenous, or recirculation phase.
                2. **Hyperfluorescence**: Distinguish Leakage (fuzzy borders), Pooling (fixed space), vs Staining.
                3. **Hypofluorescence**: Identify Blocking (blood) vs Filling Defects (ischemia).
                4. **Diagnosis**: e.g., CNVM, Ischemic CRVO, CSR.
                """

            else: # General Fallback
                specific_instruction = "Provide a formal clinical report. Structure: Findings, Impression, Recommendations."

            # The Strict System Prompt
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": f"""
                            ACT AS: Senior Consultant Ophthalmologist.
                            TONE: Professional, Clinical, Concise.
                            INSTRUCTION: Analyze the attached {task_type} image.
                            
                            STRICT RULES:
                            - Do NOT output "Step 1", "Step 2", or "Here is the analysis".
                            - Do NOT define terms (e.g., don't explain what a Visual Field is).
                            - Start directly with the Report.
                            - Use the specific format provided below.
                            
                            {specific_instruction}
                            
                            REFERENCE CONTEXT (Use if relevant): {book_text[:3000]}
                            """ 
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]

            # Call AI
            chat_completion = client.chat.completions.create(
                messages=messages,
                model="meta-llama/llama-3.2-11b-vision-preview", # Vision model
            )

            # Display Report
            st.subheader(f"📋 Clinical Report: {task_type}")
            st.markdown(chat_completion.choices[0].message.content)
            st.caption("Auto-generated by Masood Alam Eye Diagnostics. Verify clinically.")

        except Exception as e:
            st.error(f"Error: {e}")

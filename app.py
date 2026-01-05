import streamlit as st
import os
from groq import Groq
import base64
from PIL import Image
from PyPDF2 import PdfReader

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(page_title="Masood Alam Eye Diagnostics", layout="wide", page_icon="👁️")

# CSS Hack: Removes padding to make camera full-width on mobile
st.markdown("""
    <style>
        /* Remove default Streamlit padding */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
            max-width: 100%;
        }
        /* Force Camera to fill screen */
        div[data-testid="stCameraInput"] {
            width: 100% !important;
        }
        div[data-testid="stCameraInput"] video {
            width: 100% !important;
            object-fit: cover;
            border-radius: 10px;
        }
        /* Professional Report Styling */
        .report-header {
            color: #0e1117;
            font-weight: bold;
            font-size: 1.2rem;
            margin-top: 20px;
            border-bottom: 2px solid #ff4b4b;
        }
    </style>
""", unsafe_allow_html=True)

# Access API Key safely
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Security Error: API Key not found. Please set GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# --- HEADER ---
st.title("👁️ Masood Alam Eye Diagnostics")
st.markdown("### AI-Powered Ophthalmic Consultant")

# --- 2. SIDEBAR & INPUT ---
with st.sidebar:
    st.header("Select Modality")
    task_type = st.radio(
        "Modality:",
        [
            "OCT Macula",          # Separated
            "OCT ONH (Glaucoma)",  # Separated
            "Visual Field (Perimetry)", 
            "Corneal Topography", 
            "Fluorescein Angiography (FFA)", 
            "OCT Angiography (OCTA)",
            "Ultrasound B-Scan"
        ]
    )
    st.divider()
    input_method = st.radio("Input Method:", ["Upload Image File", "Use Camera"])
    
    st.info(f"Mode: **{task_type}**")
    st.caption("Powered by Llama 4 Vision (Scout)")

# --- 3. HELPER FUNCTIONS ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def get_pdf_text(filename="REFERNCE.pdf"):
    try:
        reader = PdfReader(filename)
        text = ""
        # Read first 50 pages to ensure context coverage
        for i, page in enumerate(reader.pages):
            if i > 50: break 
            text += page.extract_text()
        return text
    except FileNotFoundError:
        return "Reference text not available. Relying on internal clinical knowledge."

# --- 4. MAIN LOGIC ---
image_file = None

if input_method == "Upload Image File":
    image_file = st.file_uploader("Upload Scan", type=['png', 'jpg', 'jpeg'])
else:
    # Camera widget (now full width due to CSS above)
    image_file = st.camera_input("Capture Scan")

if image_file and st.button("Analyze Scan"):
    with st.spinner("Analyzing..."):
        try:
            client = Groq(api_key=api_key)
            base64_image = encode_image(image_file)
            book_text = get_pdf_text("REFERNCE.pdf")

            # --- DR. MASOOD'S SPECIFIC PROTOCOLS ---
            
            if task_type == "OCT Macula":
                specific_instruction = """
                **STRICT REPORT FORMAT (Macula Focus):**
                1. **Scan Quality**: Check Centration & Signal Strength.
                2. **Quantitative Analysis**:
                   - Central Subfoveal Mean Thickness (CSMT).
                   - Cube Volume / Center Point Thickness.
                3. **Morphology**: 
                   - Retinal Layers (ILM, ELM, IS/OS integrity).
                   - RPE status (Drusen, PED, Atrophy).
                4. **Pathology**: Identify Fluid (IRF/SRF), Cystoid Edema, or Traction (VMT/ERM).
                5. **Diagnosis**: e.g., AMD (Wet/Dry), DME, CSR, or Macular Hole.
                """

            elif task_type == "OCT ONH (Glaucoma)":
                specific_instruction = """
                **STRICT REPORT FORMAT (Optic Nerve Focus):**
                1. **Scan Quality**: Check Signal Strength and Disc Centration.
                2. **RNFL Analysis**: 
                   - Average Thickness (Microns).
                   - Quadrant Analysis (ISNT rule adherence).
                   - Look for thinning (Red/Yellow zones).
                3. **Optic Nerve Head (ONH)**: 
                   - Cup-to-Disc Ratio (Vertical/Horizontal).
                   - Neuroretinal Rim status.
                4. **Diagnosis**: Consistent with Glaucoma, Suspect, or Normal.
                """
            
            elif task_type == "Visual Field (Perimetry)":
                specific_instruction = """
                **STRICT REPORT FORMAT:**
                1. **Reliability Analysis**: Fixation Losses, False Pos/Neg (<33%), Trigger Happy?
                2. **Global Indices**: GHT (Outside Normal Limits?), MD, and PSD.
                3. **Visual Field Defects**: Arcuate, Nasal Step, Paracentral, or Hemianopic.
                4. **Final Clinical Interpretation**: Glaucomatous vs Neurological defect.
                """
            
            elif task_type == "Corneal Topography":
                specific_instruction = """
                **STRICT REPORT FORMAT:**
                1. **Curvature Maps**: Analyze Axial Map (Steepening patterns? K-max?).
                2. **Elevation Maps**: Check Anterior & Posterior Float (Islands of elevation >15-20µm?).
                3. **Pachymetry**: Thinnest point location & value.
                4. **Diagnosis**: Keratoconus (Inferior steepening/Asymmetric Bowtie) vs Regular Astigmatism.
                """
            
            elif task_type == "Fluorescein Angiography (FFA)":
                specific_instruction = """
                **STRICT REPORT FORMAT:**
                1. **Phase Identification**: Arterial, Arteriovenous, or Recirculation phase?
                2. **Hyperfluorescence**: Leakage, Pooling, Staining, or Window Defect.
                3. **Hypofluorescence**: Blocking or Non-perfusion (Ischemia).
                4. **Diagnosis**: CNVM, DR, Vein Occlusion, or CSR.
                """
            
            elif task_type == "OCT Angiography (OCTA)":
                specific_instruction = """
                **STRICT REPORT FORMAT:**
                1. **Vascular Zones**: Analyze Superficial, Deep, and Choriocapillaris slabs.
                2. **Pathology**: Look for Neovascular Networks (Type 1/2) or FAZ enlargement (Ischemia).
                3. **Artifacts**: Note any projection or motion artifacts.
                4. **Diagnosis**: CNV presence or Macular Ischemia.
                """

            else: 
                specific_instruction = "Provide a structured clinical report: Findings, Diagnosis, and Management Plan."

            # Master System Prompt
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": f"""
                            ACT AS: Senior Consultant Ophthalmologist (Dr. Masood Alam Shah).
                            TASK: Analyze this {task_type} scan.
                            
                            MANDATORY RULES:
                            1. Do NOT explain what the test is. Do NOT use phrases like "Step 1" or "The image shows".
                            2. Go STRAIGHT to the clinical findings using the format below.
                            3. Be concise and professional.
                            
                            {specific_instruction}
                            
                            REFERENCE CONTEXT: {book_text[:5000]}
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

            # MODEL UPDATED: Switching to Llama 4 Scout (The new 2025 Standard)
            chat_completion = client.chat.completions.create(
                messages=messages,
                model="meta-llama/llama-4-scout-17b-16e-instruct", 
            )

            # Display Report
            st.markdown("### 📋 Clinical Report")
            st.write(chat_completion.choices[0].message.content)
            st.success("Analysis Complete")

        except Exception as e:
            st.error(f"Error: {e}")

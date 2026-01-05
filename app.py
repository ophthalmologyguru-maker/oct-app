import streamlit as st
import os
from groq import Groq
import base64
from PIL import Image
from PyPDF2 import PdfReader
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Masood Alam Eye Diagnostics", layout="wide", page_icon="👁️")

# Access the API Key securely
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Security Error: API Key not found in Secrets. Please add it in Streamlit Settings.")
    st.stop()

# --- REBRANDING HEADER ---
st.title("👁️ Masood Alam Eye Diagnostics")
st.markdown("### AI-Powered Ophthalmic Consultant")
st.markdown("Select a modality from the sidebar and upload a scan for clinical analysis.")

# --- 2. SIDEBAR SELECTION ---
with st.sidebar:
    st.header("Select Modality")
    task_type = st.radio(
        "What type of image is this?",
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
    
    # --- INPUT METHOD SELECTION ---
    input_method = st.radio("Choose Input Method:", ["Upload Image File", "Use Camera"])
    
    st.info(f"Currently Analyzing: **{task_type}**")
    st.caption("Powered by Llama 4 Vision & Groq")

# --- 3. HELPER FUNCTIONS ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def get_pdf_text(filename="REFERNCE.pdf"):
    try:
        reader = PdfReader(filename)
        text = ""
        # Read first 45 pages to capture key diagnostic criteria
        for i, page in enumerate(reader.pages):
            if i > 45: break 
            text += page.extract_text()
        return text
    except FileNotFoundError:
        return "Error: REFERNCE.pdf not found. Please ensure the file is named exactly 'REFERNCE.pdf' in GitHub."

# --- 4. MAIN LOGIC ---

# Smart Input Handling
image_file = None

if input_method == "Upload Image File":
    image_file = st.file_uploader("Upload Patient Image", type=['png', 'jpg', 'jpeg'])
else:
    # This widget works INSIDE the browser, preventing the 'refresh' crash on mobile
    image_file = st.camera_input("Take a Photo of the Scan")

if image_file and st.button("Analyze Scan"):
    with st.spinner(f"Consulting AI about {task_type}..."):
        try:
            client = Groq(api_key=api_key)

            # Encode Image directly from the file object
            base64_image = encode_image(image_file)
            
            # Get Context from the book
            book_text = get_pdf_text("REFERNCE.pdf")

            # --- CUSTOM PROMPTS FOR EACH MODULE ---
            if task_type == "OCT (Retina)":
                specific_instruction = "Analyze this OCT scan. Identify layers (ILM, RPE), look for fluid (SRF, IRF), PEDs, or atrophy. Differentiate between wet AMD and DME features."
            
            elif task_type == "Visual Field (Perimetry)":
                specific_instruction = "Analyze this Humphrey Visual Field. Identify the pattern (e.g., arcuate defect, nasal step, central island). Assess reliability indices (fixation losses, false positives) and determine if the defect aligns with glaucoma or neurological issues."
            
            elif task_type == "Corneal Topography":
                specific_instruction = "Analyze this Pentacam/Topography map. Look for steepening patterns (Keratoconus, pellucid marginal degeneration), astigmatism type (with/against the rule), and pachymetry thinning."
            
            elif task_type == "Fluorescein Angiography (FFA)":
                specific_instruction = "Analyze this FFA image. Identify the phase (arterial, venous, recirculation). Look for Hyperfluorescence (leakage, pooling, staining, window defects) or Hypofluorescence (blocking, filling defects). Differentiate between CNV leakage and staining drusen."
            
            elif task_type == "OCT Angiography (OCTA)":
                specific_instruction = "Analyze this OCT Angiography (OCTA) scan. Look for capillary dropout (ischemia), enlargement of the FAZ (foveal avascular zone), or presence of neovascular networks (Type 1, 2, or 3). Distinguish between flow voids and artifacts."
            
            elif task_type == "Ultrasound B-Scan":
                specific_instruction = "Analyze this B-Scan. Look for retinal detachment (undulating membrane), vitreous hemorrhage, posterior vitreous detachment, or choroidal masses (melanoma vs nevus reflectivity)."

            # The Master Prompt
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": f"You are an expert Consultant Ophthalmologist at Masood Alam Eye Diagnostics. Use the provided text as your primary knowledge base.\n\nTask: {specific_instruction}\n\nReference Knowledge: {book_text[:6000]}..." 
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

            # Send to Llama 4
            chat_completion = client.chat.completions.create(
                messages=messages,
                model="meta-llama/llama-4-scout-17b-16e-instruct", 
            )

            st.subheader(f"Analysis: {task_type}")
            st.success("Report Generated by Masood Alam Eye Diagnostics AI")
            st.write(chat_completion.choices[0].message.content)

        except Exception as e:
            st.error(f"An error occurred: {e}")

import streamlit as st
import os
from groq import Groq
import base64
from PIL import Image
from PyPDF2 import PdfReader

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Ophthalmology AI Consultant", layout="wide", page_icon="👁️")

# Access the API Key securely from Streamlit Secrets
# (Make sure you set GROQ_API_KEY in the app settings!)
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Security Error: API Key not found in Secrets.")
    st.stop()

st.title("👁️ AI Ophthalmology Consultant")
st.markdown("Upload a scan below. The AI will analyze it based on standard clinical guidelines.")

# --- 2. SIDEBAR SELECTION ---
with st.sidebar:
    st.header("Select Modality")
    task_type = st.radio(
        "What type of image is this?",
        ["OCT (Retina)", "Visual Field (Perimetry)", "Corneal Topography", "Ultrasound B-Scan"]
    )
    
    st.info(f"Currently Analyzing: **{task_type}**")
    st.divider()
    st.caption("Powered by Llama 4 Vision & Groq")

# --- 3. HELPER FUNCTIONS ---
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_pdf_text(filename="reference.pdf"):
    """Reads the 'baked-in' textbook from GitHub"""
    try:
        reader = PdfReader(filename)
        text = ""
        # Read first 30 pages (enough for context without crashing)
        for i, page in enumerate(reader.pages):
            if i > 30: break 
            text += page.extract_text()
        return text
    except FileNotFoundError:
        return "Error: reference.pdf not found. Please upload it to GitHub."

# --- 4. MAIN LOGIC ---
uploaded_image = st.file_uploader("Upload Patient Image", type=['png', 'jpg', 'jpeg'])

if uploaded_image and st.button("Analyze Scan"):
    with st.spinner(f"Consulting AI about {task_type}..."):
        try:
            client = Groq(api_key=api_key)

            # Save and Encode Image
            with open("temp_scan.jpg", "wb") as f:
                f.write(uploaded_image.getbuffer())
            base64_image = encode_image("temp_scan.jpg")
            
            # Get Context from the book
            book_text = get_pdf_text("reference.pdf")

            # Custom Prompts for each specialty
            if task_type == "OCT (Retina)":
                specific_instruction = "Analyze this OCT. Describe layers (ILM, RPE), identify fluid (SRF, IRF), holes, or atrophy."
            elif task_type == "Visual Field (Perimetry)":
                specific_instruction = "Analyze this Humphrey Visual Field. Look for Pattern Deviation defects, Glaucoma Hemifield Test (GHT) status, and describe any scotomas (arcuate, nasal step, etc)."
            elif task_type == "Corneal Topography":
                specific_instruction = "Analyze this Pentacam/Topography map. Look for steepening (Keratoconus), astigmatism patterns (Bowtie), and thickness (Pachymetry)."
            elif task_type == "Ultrasound B-Scan":
                specific_instruction = "Analyze this B-Scan. Look for retinal detachment, vitreous hemorrhage, posterior vitreous detachment, or intraocular masses."

            # The Master Prompt
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": f"You are an expert Consultant Ophthalmologist. Use the provided text as a knowledge base.\n\nTask: {specific_instruction}\n\nReference Text: {book_text[:2000]}..." # We send a snippet of text to save memory
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

            st.subheader("Clinical Analysis")
            st.write(chat_completion.choices[0].message.content)

        except Exception as e:
            st.error(f"An error occurred: {e}")

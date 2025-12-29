import streamlit as st
import google.generativeai as genai
from PIL import Image
import tempfile
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="OCT Expert AI", page_icon="👁️", layout="wide")

st.title("👁️ AI Optical Coherence Tomography (OCT) Analyst")
st.markdown("""
This tool uses **Gemini 2.5 Flash** to analyze OCT scans based on your reference textbooks.
""")

# --- SIDEBAR: SETUP ---
with st.sidebar:
    st.header("1. Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    
    st.header("2. Knowledge Base")
    st.info("Upload your OCT Textbook or Guidelines here. The AI will read this to form its opinion.")
    uploaded_book = st.file_uploader("Upload Reference PDF", type=['pdf'])

    st.divider()
    st.markdown("**Model:** Gemini 2.5 Flash (2025 Edition)")

# --- MAIN APP LOGIC ---

def analyze_oct(image, pdf_path, prompt_text):
    """Sends the image + pdf + prompt to Gemini"""
    try:
        # Configure the AI with your API Key
        genai.configure(api_key=api_key)
        
        # Use the specific Gemini 2.5 Flash model
        model = genai.GenerativeModel('gemini-2.5-flash') 

        # Upload the PDF to Gemini's temporary storage
        with st.spinner("Reading textbook... (This happens once per file)"):
            pdf_file = genai.upload_file(pdf_path)
        
        # Prepare the Prompt
        # We send the PDF (Knowledge), the Image (Patient), and the Text (Instruction)
        response = model.generate_content([
            prompt_text, 
            pdf_file, 
            image
        ])
        return response.text
        
    except Exception as e:
        return f"Error: {str(e)}"

# --- USER INTERFACE ---

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Patient Data")
    uploaded_image = st.file_uploader("Upload OCT Scan Image", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Patient Scan", use_column_width=True)

with col2:
    st.subheader("AI Analysis")
    
    # The "System Instruction" / Persona
    system_prompt = st.text_area(
        "AI Instructions (Editable)", 
        value="You are an expert Consultant Ophthalmologist. Analyze the attached OCT scan based STRICTLY on the attached PDF textbook. \n\n1. Describe the retinal layers (ILM, RPE, IS/OS junction, etc).\n2. Identify any pathology (e.g., SRF, IRF, PED, disruption).\n3. Suggest a diagnosis referencing the textbook chapters.",
        height=150
    )

    if st.button("Analyze Scan", type="primary"):
        if not api_key:
            st.error("Please enter your API Key in the sidebar.")
        elif not uploaded_book:
            st.error("Please upload a Reference PDF (Textbook) in the sidebar.")
        elif not uploaded_image:
            st.error("Please upload an OCT image.")
        else:
            # Save the uploaded PDF temporarily so Gemini can read it
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                tmp_pdf.write(uploaded_book.getvalue())
                tmp_pdf_path = tmp_pdf.name

            # Run Analysis
            with st.spinner("Analyzing layers and consulting the textbook..."):
                result = analyze_oct(image, tmp_pdf_path, system_prompt)
                st.markdown(result)
            
            # Cleanup temp file
            os.remove(tmp_pdf_path)

import streamlit as st
import google.generativeai as genai
from PIL import Image
import tempfile
import os

# 1. Setup the Page
st.set_page_config(page_title="OCT Expert AI", layout="wide")
st.title("OCT Analysis Tool")

# 2. Sidebar Inputs
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Google API Key", type="password")
uploaded_file = st.sidebar.file_uploader("Upload Textbook PDF", type=['pdf'])
st.sidebar.info("Model: Gemini 1.5 Flash (Standard Free)")

# 3. Main Area Input
st.write("### Upload Patient Scan")
uploaded_image = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])

# 4. The Logic
if st.button("Analyze Scan"):
    if not api_key or not uploaded_file or not uploaded_image:
        st.error("❌ Please provide API Key, PDF, and Image.")
    else:
        try:
            with st.spinner("Analyzing with Gemini 1.5 Flash..."):
                genai.configure(api_key=api_key)
                
                # REVERTED: Switching back to the stable 1.5 model
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Save PDF
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                # Analyze
                pdf_blob = genai.upload_file(tmp_path)
                image_blob = Image.open(uploaded_image)
                
                prompt = "You are an expert Ophthalmologist. Analyze this OCT scan based on the attached textbook. Describe layers, pathology, and diagnosis."
                
                response = model.generate_content([prompt, pdf_blob, image_blob])
                
                st.success("Analysis Complete")
                st.markdown(response.text)
                
                os.remove(tmp_path)
                
        except Exception as e:
            st.error(f"Error: {e}")

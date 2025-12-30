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
st.sidebar.info("Model: Gemini 1.5 Flash")

# 3. Main Area Input
st.write("### Upload Patient Scan")
uploaded_image = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])

# 4. The Logic
if st.button("Analyze Scan"):
    # Check if everything is there
    if not api_key:
        st.error("❌ Missing API Key. Check the sidebar.")
    elif not uploaded_file:
        st.error("❌ Missing Reference PDF. Check the sidebar.")
    elif not uploaded_image:
        st.error("❌ Missing Patient Image.")
    else:
        # If everything is ready, run the AI
        try:
            with st.spinner("Analyzing..."):
                # Configure AI
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Save PDF temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                # Send to Gemini
                pdf_blob = genai.upload_file(tmp_path)
                image_blob = Image.open(uploaded_image)
                
                prompt = "You are an expert Ophthalmologist. Analyze this OCT scan based on the attached textbook. Describe layers, pathology, and diagnosis."
                
                response = model.generate_content([prompt, pdf_blob, image_blob])
                
                # Show Result
                st.success("Analysis Complete")
                st.markdown(response.text)
                
                # Cleanup
                os.remove(tmp_path)
                
        except Exception as e:
            st.error(f"An error occurred: {e}")

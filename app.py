import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import nltk
import re
import syllapy
from io import BytesIO
from webdriver_manager.chrome import ChromeDriverManager

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(nltk.corpus.stopwords.words('english'))

# Set Streamlit layout to wide mode
st.set_page_config(layout="wide")

# Streamlit Title
st.title("🚀 Advanced Article Text Analysis Platform 🚀")
st.markdown("""
### 📝 Introduction
Welcome to the **Advanced Article Text Analysis Platform**, your ultimate tool for extracting, processing and analyzing articles from URLs. This platform is tailored for researchers, analysts and content creators who need detailed insights into textual data.

The application leverages cutting-edge technologies such as **web scraping** and **natural language processing (NLP)** to compute key metrics like sentiment scores, readability and linguistic characteristics. It automates the tedious tasks of manual article analysis and ensures accurate, structured output.

### 🎯 Key Objectives
The primary goals of this platform are to:
1. **Extract Content**: Automatically retrieve titles and body text from articles hosted at URLs provided in an input Excel file.
2. **Analyze Text**: Perform in-depth analysis to compute key variables such as:
   - **Positive Score** and **Negative Score** for sentiment analysis.
   - **Fog Index** and **Average Sentence Length** for readability.
   - **Word Count**, **Complex Words**, and other linguistic features.
3. **Generate Results**: Provide a live preview of computed results and enable easy download of the final structured data.

### ⚡ Why Use This Platform?
- **🔄 Automation**: Eliminates the need for manual data collection and analysis.
- **🎯 Precision**: Computes metrics based on proven linguistic and readability formulas.
- **🖥️ User-Friendly**: Intuitive interface for uploading files, viewing live results and downloading outputs.
- **🔧 Customizable**: Allows users to modify the positive and negative word dictionaries for specific use cases.

---

""")

# Custom CSS for background hover effect and button colors
st.markdown(""" 
    <style>
        body {
            background: linear-gradient(135deg, rgba(255,0,0,0.7), rgba(0,0,255,0.7));
            transition: background-color 0.5s ease;
        }
        .stButton > button:hover {
            background-color: rgba(255, 165, 0, 0.8);
            color: white;
        }
        .stButton > button {
            background-color: rgba(0, 255, 0, 0.7);
            color: black;
            border: none;
            border-radius: 5px;
            padding: 10px 15px;
            font-size: 16px;
            transition: background-color 0.3s, transform 0.3s;
        }
        .stButton > button:active {
            transform: scale(0.95);
        }
        .creator-link {
            color: black;
            font-size: 16px;
            font-weight: bold;
            text-decoration: none;
            display: block;  
            text-align: center;  
            margin-top: 10px;   
        }
        .creator-link:hover {
            background-color: white;  
            color: red;              
            padding: 5px;           
            border-radius: 5px;     
        }
    </style>
""", unsafe_allow_html=True)

# Creator link at the top of the sidebar
st.markdown(
    '<a href="https://www.linkedin.com/in/sm980/" class="creator-link">Created by SHASHWAT MISHRA</a>',
    unsafe_allow_html=True
)

# File Upload Instructions
if st.radio("❓ Do you want to see the file upload instructions?", ("Yes", "No")) == "Yes":
    st.write("""
    ### 📂 File Upload Instructions:
    Please upload the following files to proceed:
    
    1️⃣ **Input Excel File** (`Input.xlsx`):
        - Must include columns `URL_ID` and `URL`.

    2️⃣ **Positive Words File** (`positive-words.txt`).
    
    3️⃣ **Negative Words File** (`negative-words.txt`).
    """)

# File Uploaders
input_file = st.file_uploader("📥 Upload Input Excel File", type=["xlsx"])
positive_file = st.file_uploader("📥 Upload Positive Words File", type=["txt"])
negative_file = st.file_uploader("📥 Upload Negative Words File", type=["txt"])

# Validate Uploads
if not (input_file and positive_file and negative_file):
    st.warning("⚠️ Please upload all required files.")
    st.stop()

# Load Files
input_df = pd.read_excel(input_file)

# Robust File Decoding for Positive Words
try:
    positive_words = set(positive_file.read().decode('utf-8').splitlines())
except UnicodeDecodeError:
    positive_file.seek(0)  # Reset the file pointer to the start
    positive_words = set(positive_file.read().decode('ISO-8859-1').splitlines())

# Robust File Decoding for Negative Words
try:
    negative_words = set(negative_file.read().decode('utf-8').splitlines())
except UnicodeDecodeError:
    negative_file.seek(0)  # Reset the file pointer to the start
    negative_words = set(negative_file.read().decode('ISO-8859-1').splitlines())

# Initialize Selenium WebDriver
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920x1080')
options.add_argument('--disable-dev-shm-usage')  # Add this line
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Functions
def clean_text(text):
    words = nltk.word_tokenize(text.lower())
    return [word for word in words if word.isalpha() and word not in stop_words]

def analyze_text(text):
    words = clean_text(text)
    positive_score = sum(1 for word in words if word in positive_words)
    negative_score = sum(1 for word in words if word in negative_words)
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (len(words) + 0.000001)
    sentences = nltk.sent_tokenize(text)
    avg_sentence_length = len(words) / len(sentences) if sentences else 0
    complex_words = [word for word in words if syllapy.count(word) >= 3]
    percentage_complex_words = len(complex_words) / len(words) * 100 if words else 0
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)
    word_count = len(words)
    avg_word_length = sum(len(word) for word in words) / word_count if word_count else 0

    return {
        'Positive Score': positive_score,
        'Negative Score': negative_score,
        'Polarity Score': polarity_score,
        'Subjectivity Score': subjectivity_score,
        'Average Sentence Length': avg_sentence_length,
        'Percentage of Complex Words': percentage_complex_words,
        'Fog Index': fog_index,
        'Word Count': word_count,
        'Average Word Length': avg_word_length,
    }

def summarize_text(text):
    sentences = nltk.sent_tokenize(text)
    if len(sentences) > 5:
        return ' '.join(sentences[:5])  # Return the first 5 sentences as a summary
    return text  # If the text is short, return it as is

def extract_article(url, url_id):
    try:
        driver.get(url)
        time.sleep(3)
        title = driver.title.strip() if driver.title else "No Title"
        paragraphs = driver.find_elements(By.TAG_NAME, 'p')
        article_text = ' '.join([p.text.strip() for p in paragraphs if p.text.strip()])
        summary = summarize_text(article_text)
        return title, summary
    except Exception as e:
        st.error(f"❌ Error extracting {url}: {e}")
        return None, None

# Analysis Button
results = []
output_buffer = BytesIO()
if st.button("🚀 Start Analysis"):
    for idx, row in input_df.iterrows():
        processing_no = idx + 1
        url_id, url = row['URL_ID'], row['URL']
        st.info(f"🔄 Processing No: {processing_no} | URL_ID: {url_id} | URL: {url}")
        title, summary = extract_article(url, url_id)
        if summary:
            st.write(f"**Title:** {title}")
            st.write(f"**Description:** {summary}")  # Display the summary of the article
            analysis = analyze_text(summary)
            analysis.update({'Processing No': processing_no, 'URL_ID': url_id, 'URL': url, 'Title': title})
            results.append(analysis)
            results_df = pd.DataFrame(results)
            st.dataframe(results_df)  # Live Preview
            with pd.ExcelWriter(output_buffer, engine='xlsxwriter') as writer:
                results_df.to_excel(writer, index=False, sheet_name='Results')
            output_buffer.seek(0)
    st.success("✅ Analysis Complete!")
    st.download_button("📥 Download Results", output_buffer, "Output_Data_Structure.xlsx")

driver.quit()

import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import nltk
import re
import syllapy
from webdriver_manager.chrome import ChromeDriverManager
from io import BytesIO

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(nltk.corpus.stopwords.words('english'))

# Set the layout to wide mode
st.set_page_config(layout="wide")

# Streamlit title
st.title("🌟 Advanced Article Text Analysis Platform 🌟")
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

# Option for file upload instructions
show_instructions = st.radio("Do you want to see the file upload instructions?", ("Yes", "No"))

if show_instructions == "Yes":
    st.write(""" ### 📁 File Upload Instructions
    To initiate the analysis, please upload the following files:
    ---
    1. **Input Excel File (`Input.xlsx`)**:
       - **📝 Description**: This file should contain a list of URLs to be analyzed for text content.
       - **📊 Format**: It must have the following columns:
         - **`URL_ID`**: A unique identifier for each URL.
         - **`URL`**: The complete URL of the article you wish to analyze. Please ensure that each URL is valid and accessible.
       - **🔍 Example**:
       ```
       | URL_ID | URL                           |
       |--------|-------------------------------|
       | 1      | https://example.com/article1  |
       | 2      | https://example.com/article2  |
       ```
    ---
    2. **Positive Words File (`positive-words.txt`)**:
       - **📄 Description**: This text file should include a list of positive words for sentiment analysis.
       - **📜 Format**: Each line should contain a single positive word.
       - **✨ Example**:
       ```
       excellent
       joyful
       remarkable
       ```
    ---
    3. **Negative Words File (`negative-words.txt`)**:
       - **📉 Description**: This text file should include a list of negative words for sentiment analysis.
       - **📝 Format**: Each line should contain a single negative word.
       - **⚠️ Example**:
       ```
       terrible
       sad
       awful
       ```
    ---
    ### 🚀 Ready to Analyze?
    Once you have prepared and uploaded these files, click the **"Analyze"** button below to start the text analysis process! Your results will be generated in real-time and can be downloaded after processing.
    ### 📁 Example Files
    You can download example files below to help you get started:
    """)

    # Create example DataFrame for the Input Excel file
    example_input_df = pd.DataFrame({
        'URL_ID': [1, 2],
        'URL': ['https://example.com/article1', 'https://example.com/article2']
    })

    # Create example positive words
    example_positive_words = """excellent
    joyful
    remarkable
    """

    # Create example negative words
    example_negative_words = """terrible
    sad
    awful
    """

    # Create a BytesIO object for the input Excel file
    example_input = BytesIO()
    with pd.ExcelWriter(example_input, engine='xlsxwriter') as writer:
        example_input_df.to_excel(writer, index=False, sheet_name='Sheet1')
    example_input.seek(0)  # Reset pointer to the beginning

    # Download buttons for example files
    st.download_button("Download Example Input Excel File", example_input, "example_input.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("Download Example Positive Words File", example_positive_words.encode('utf-8'), "example_positive_words.txt", "text/plain")
    st.download_button("Download Example Negative Words File", example_negative_words.encode('utf-8'), "example_negative_words.txt", "text/plain")

# File uploader for Input.xlsx
input_file = st.file_uploader("Upload the Input Excel file", type=["xlsx"])
if input_file is not None:
    input_df = pd.read_excel(input_file)
else:
    st.warning("Please upload the Input Excel file.")
    st.stop()  # Stop the script if no file is uploaded

# File uploader for positive words
positive_file = st.file_uploader("Upload the Positive Words file", type=["txt"])
if positive_file is not None:
    try:
        positive_words = set(positive_file.read().decode('utf-8').splitlines())
    except UnicodeDecodeError:
        positive_file.seek(0)  # Reset file pointer to the start
        positive_words = set(positive_file.read().decode('ISO-8859-1').splitlines())
else:
    st.warning("Please upload the Positive Words file.")
    st.stop()  # Stop the script if no file is uploaded

# File uploader for negative words
negative_file = st.file_uploader("Upload the Negative Words file", type=["txt"])
if negative_file is not None:
    try:
        negative_words = set(negative_file.read().decode('utf-8').splitlines())
    except UnicodeDecodeError:
        negative_file.seek(0)  # Reset file pointer to the start
        negative_words = set(negative_file.read().decode('ISO-8859-1').splitlines())
else:
    st.warning("Please upload the Negative Words file.")
    st.stop()  # Stop the script if no file is uploaded

# Initialize the Selenium WebDriver in headless mode
options = webdriver.ChromeOptions()
options.headless = True  # Run in headless mode (no browser window)
options.add_argument('--disable-gpu')  # Disables GPU hardware acceleration
options.add_argument('--no-sandbox')  # Bypass OS security model for running in container environments
options.add_argument('--window-size=1920x1080')  # Set window size

chrome_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=chrome_service, options=options)

# Function to extract article text using Selenium
def extract_article(url, url_id):
    try:
        driver.get(url)
        time.sleep(3)  # Allow the page to load, increase if necessary

        title = driver.title.strip() if driver.title else "No Title"

        # Extract text from all paragraphs using Selenium
        paragraphs = driver.find_elements(By.TAG_NAME, 'p')
        article_text = ' '.join([p.text.strip() for p in paragraphs if p.text.strip()])

        if len(article_text) == 0:
            st.write(f"No content found at {url}.")
            return title, None

        return title, article_text
    except Exception as e:
        st.write(f"Error extracting {url}: {e}")
        return None, None

# Function to clean text and remove stopwords
def clean_text(text):
    words = nltk.word_tokenize(text.lower())
    words = [word for word in words if word.isalpha() and word not in stop_words]
    return words

# Function to perform text analysis
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
    avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
    complex_word_count = len(complex_words)
    word_count = len(words)
    syllables_per_word = sum(syllapy.count(word) for word in words) / word_count if word_count else 0
    personal_pronouns = [word for word in words if word in ['i', 'me', 'my', 'mine', 'you', 'your', 'yours', 'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its', 'we', 'us', 'our', 'ours', 'they', 'them', 'their', 'theirs']]
    avg_word_length = sum(len(word) for word in words) / word_count if word_count else 0

    return {
        'Positive Score': positive_score,
        'Negative Score': negative_score,
        'Polarity Score': polarity_score,
        'Subjectivity Score': subjectivity_score,
        'Average Sentence Length': avg_sentence_length,
        'Percentage of Complex Words': percentage_complex_words,
        'Fog Index': fog_index,
        'Average Number of Words per Sentence': avg_words_per_sentence,
        'Complex Word Count': complex_word_count,
        'Word Count': word_count,
        'Syllables per Word': syllables_per_word,
        'Personal Pronouns': len(personal_pronouns),
        'Average Word Length': avg_word_length
    }

# Button to trigger analysis
if st.button("Analyze"):
    results = []
    
    for index, row in input_df.iterrows():
        url_id = row['URL_ID']
        url = row['URL']
        title, article_text = extract_article(url, url_id)
        
        if article_text:
            analysis = analyze_text(article_text)
            analysis['URL ID'] = url_id
            analysis['URL'] = url
            analysis['Title'] = title
            results.append(analysis)

    if results:
        results_df = pd.DataFrame(results)

        # Show results in Streamlit
        st.subheader("🔍 Analysis Results")
        st.dataframe(results_df)

        # Create a BytesIO object for the results DataFrame
        output_data = BytesIO()
        with pd.ExcelWriter(output_data, engine='xlsxwriter') as writer:
            results_df.to_excel(writer, index=False, sheet_name='Analysis Results')
        output_data.seek(0)  # Reset pointer to the beginning

        # Download button for results
        st.download_button("Download Analysis Results", output_data, "analysis_results.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # Close the driver after analysis
    driver.quit()

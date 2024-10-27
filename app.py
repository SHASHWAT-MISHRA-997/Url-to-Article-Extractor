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

# Initialize the Selenium WebDriver with updated options
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode
options.add_argument('--no-sandbox')  # Bypass OS security model
options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
options.add_argument('--window-size=1920x1080')  # Set window size

chrome_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=chrome_service, options=options)

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
            display: block;  /* Make the link a block element */
            text-align: center;  /* Center text */
            margin-top: 10px;   /* Add some space above */
        }
        .creator-link:hover {
            background-color: white;  /* Background color on hover */
            color: red;              /* Change text color on hover */
            padding: 5px;           /* Add some padding on hover */
            border-radius: 5px;     /* Rounded corners */
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
    st.write("""
    ### 📁 File Upload Instructions
    To initiate the analysis, please upload the following files:
    
    ---
    
    1. **Input Excel File (`Input.xlsx`)**:
       - **📝 Description**: This file should contain a list of URLs to be analyzed for text content.
       - **📊 Format**: It must have the following columns:
         - **`URL_ID`**: A unique identifier for each URL. This can be any alphanumeric string (e.g., 1, 2, 3, or ID001, ID002).
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
       - **📄 Description**: This text file should include a list of positive words that contribute to positive sentiment analysis.
       - **📜 Format**: Each line should contain a single positive word (e.g., "excellent", "joyful").
       - **✨ Example**:
       ```
       excellent
       joyful
       remarkable
       ```
    
    ---
    
    3. **Negative Words File (`negative-words.txt`)**:
       - **📉 Description**: This text file should include a list of negative words that contribute to negative sentiment analysis.
       - **📝 Format**: Each line should contain a single negative word (e.g., "terrible", "sad").
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
        # Attempt to read the file with utf-8 encoding
        positive_words = set(positive_file.read().decode('utf-8').splitlines())
    except UnicodeDecodeError:
        # If there's a decode error, try another encoding
        positive_file.seek(0)  # Reset file pointer to the start
        positive_words = set(positive_file.read().decode('ISO-8859-1').splitlines())
else:
    st.warning("Please upload the Positive Words file.")
    st.stop()  # Stop the script if no file is uploaded

# File uploader for negative words
negative_file = st.file_uploader("Upload the Negative Words file", type=["txt"])
if negative_file is not None:
    try:
        # Attempt to read the file with utf-8 encoding
        negative_words = set(negative_file.read().decode('utf-8').splitlines())
    except UnicodeDecodeError:
        # If there's a decode error, try another encoding
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
    complex_words = [word for word in words if syllapy.count(word) > 2]
    percentage_complex_words = len(complex_words) / len(words) if words else 0
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)
    word_count = len(words)
    complex_word_count = len(complex_words)
    syllable_count = sum(syllapy.count(word) for word in words)
    syllables_per_word = syllable_count / len(words) if words else 0
    personal_pronouns = re.findall(r'\b(I|we|my|ours|us)\b', text, re.I)
    personal_pronoun_count = len(personal_pronouns)
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    
    return {
        "Positive Score": positive_score,
        "Negative Score": negative_score,
        "Polarity Score": polarity_score,
        "Subjectivity Score": subjectivity_score,
        "Avg Sentence Length": avg_sentence_length,
        "Percentage of Complex Words": percentage_complex_words,
        "Fog Index": fog_index,
        "Complex Word Count": complex_word_count,
        "Word Count": word_count,
        "Syllables Per Word": syllables_per_word,
        "Personal Pronouns": personal_pronoun_count,
        "Avg Word Length": avg_word_length
    }

# Output DataFrame columns
output_columns = [
    'URL_ID', 'URL', 'POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE', 'SUBJECTIVITY SCORE',
    'AVG SENTENCE LENGTH', 'PERCENTAGE OF COMPLEX WORDS', 'FOG INDEX', 'COMPLEX WORD COUNT',
    'WORD COUNT', 'SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 'AVG WORD LENGTH'
]
output_df = pd.DataFrame(columns=output_columns)

# Placeholder for live results
live_results_placeholder = st.empty()

# Process each URL
for index, row in input_df.iterrows():
    serial_number = index + 1
    st.write(f"Serial No. {serial_number}: Processing URL ID {row['URL_ID']}...")  # Show serial number with processing
    title, article_text = extract_article(row['URL'], row['URL_ID'])
    
    if article_text:
        # Display the extracted article and URL
        live_results_placeholder.subheader(f"URL: {row['URL']}")
        live_results_placeholder.write(f"Title: {title}")
        live_results_placeholder.write(article_text[:500] + '...')  # Show first 500 characters of the article
        
        # Display the extracted article and URL
        st.subheader(f"URL: {row['URL']}")
        st.write(f"Title: {title}")
        st.write(article_text[:500] + '...')  # Show first 500 characters of the article
        
        analysis_results = analyze_text(article_text)
        row_data = pd.DataFrame([{
            'URL_ID': row['URL_ID'],
            'URL': row['URL'],
            'POSITIVE SCORE': analysis_results['Positive Score'],
            'NEGATIVE SCORE': analysis_results['Negative Score'],
            'POLARITY SCORE': analysis_results['Polarity Score'],
            'SUBJECTIVITY SCORE': analysis_results['Subjectivity Score'],
            'AVG SENTENCE LENGTH': analysis_results['Avg Sentence Length'],
            'PERCENTAGE OF COMPLEX WORDS': analysis_results['Percentage of Complex Words'],
            'FOG INDEX': analysis_results['Fog Index'],
            'COMPLEX WORD COUNT': analysis_results['Complex Word Count'],
            'WORD COUNT': analysis_results['Word Count'],
            'SYLLABLE PER WORD': analysis_results['Syllables Per Word'],
            'PERSONAL PRONOUNS': analysis_results['Personal Pronouns'],
            'AVG WORD LENGTH': analysis_results['Avg Word Length']
        }])
        
        output_df = pd.concat([output_df, row_data], ignore_index=True)

# Update the placeholder with live results
        live_results_placeholder.dataframe(output_df)

# Save final results to Excel and create a download link
output_file_path = 'Output_Results.xlsx'
output_df.to_excel(output_file_path, index=False)

# Provide download link for the output Excel file
st.download_button(
    label="Download Results as Excel",
    data=open(output_file_path, 'rb'),
    file_name='Output_Results.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

# Close the browser at the end
driver.quit()

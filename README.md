# Url-to-Article-Extractor

🌟 Advanced Article Text Analysis Platform 🌟
This platform provides a comprehensive text analysis of articles extracted from URLs. Using Streamlit, Selenium, and NLTK, it computes sentiment scores, readability indices, and other text metrics, outputting results in a downloadable Excel file.

# 📋 Features

Automated Web Scraping: Uses Selenium to extract article content from provided URLs.
Sentiment Analysis: Calculates positive and negative sentiment scores based on user-uploaded word lists.
Readability and Complexity Metrics: Computes Fog Index, percentage of complex words, average sentence length, and more.
Real-Time Analysis Display: Shows extracted content and analysis results for each URL as they are processed.
Downloadable Results: Saves analysis data into an Excel file that can be downloaded.

# 📂 File Requirements
To use the platform, you need to upload the following files:

Input Excel File (Input.xlsx):

Should contain the URLs for analysis, with columns: URL_ID (unique identifier) and URL (full link to the article).
Example:
arduino
Copy code
| URL_ID | URL                           |
|--------|-------------------------------|
| 1      | https://example.com/article1  |
| 2      | https://example.com/article2  |
Positive Words File (positive-words.txt):

List of words considered positive, one per line.
Negative Words File (negative-words.txt):

List of words considered negative, one per line.
Example files are available for download in the app interface.

# 🔧 Installation

Clone the Repository: Clone this repository to your local machine.

bash
Copy code
git clone <repository_url>
cd Url-to-Article-Extractor
Install Dependencies: Install Python dependencies.

bash
Copy code
pip install -r requirements.txt
Set up NLTK Resources: Download necessary resources for NLTK.

python
Copy code
import nltk
nltk.download('punkt')
nltk.download('stopwords')
Start the Streamlit App: Run the Streamlit application.

bash
Copy code
streamlit run app.py

# 🚀 Usage

Launch the Streamlit application using the command above.
Follow the upload instructions and upload the required files.
Click the Analyze button to begin processing.
Download the results using the provided link.

# 🛠️ Additional Information

Headless Mode: This app uses a headless Chrome WebDriver to load and extract content from URLs without a visible browser window.
Error Handling: If any error occurs during extraction, the app skips the URL and displays an error message.

# ✨ Example Output

The output file Output_Results.xlsx contains the following columns:

POSITIVE SCORE
NEGATIVE SCORE
POLARITY SCORE
SUBJECTIVITY SCORE
AVG SENTENCE LENGTH
PERCENTAGE OF COMPLEX WORDS
FOG INDEX
COMPLEX WORD COUNT
WORD COUNT
SYLLABLE PER WORD
PERSONAL PRONOUNS
AVG WORD LENGTH

# 🖥️ Technologies Used

Python: Core language
Streamlit: Interface for user interaction and displaying results
Selenium: Web scraping for article extraction
NLTK: Natural language processing toolkit
syllapy: Syllable counter for readability metrics

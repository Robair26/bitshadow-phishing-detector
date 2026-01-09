# 🧪 Testing Instructions for AI Phishing Email Detector

This document provides detailed instructions on how to test the **AI Phishing Email Detector** locally using various types of input files such as `.txt`, `.eml`, and `.pdf`.

## 🚀 Test Cases

### 1. Upload a `.txt` file with a normal message
- Test Case: `normal_email.txt`
- Expected Outcome: The email should be classified as **safe**.
- This test checks if the detector can handle simple email content without any phishing clues.

### 2. Upload a phishing-style `.txt` file
- Test Case: `phishing_email.txt`
- Expected Outcome: The email should be classified as **phishing**.
- This test checks if the detector correctly identifies phishing content based on keywords and social engineering cues.

### 3. Upload a `.pdf` or `.eml` file to test parsing
- Test Case: `test_email.eml` or `test_email.pdf`
- Expected Outcome: The email content should be extracted and analyzed correctly.
- This test ensures the detector works with different file formats, including `.eml` and `.pdf`.

### 4. Toggle the "Verbose Output" option
- This setting provides detailed insights into the language detection, translation, link scanning, and phishing detection process.
- It helps track which parts of the content are triggering detection mechanisms.

## ⚙️ How to Test Locally

Follow these steps to test the tool locally using the provided test cases:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Robair26/ai-phishing-detector.git
    cd ai-phishing-detector
    ```

2. **Set up the environment**:
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    pip install -r requirements.txt
    ```

3. **Run the Streamlit app**:
    ```bash
    streamlit run app.py
    ```

4. **Test the uploaded files**:
    - Upload the `.txt`, `.eml`, and `.pdf` files in the Streamlit UI for analysis.

5. **Check the output**:
    - Review the **classification results** to verify if the tool correctly detects phishing or safe emails.

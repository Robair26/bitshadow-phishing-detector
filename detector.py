import os
import re
import logging
import requests
from langdetect import detect
from deep_translator import GoogleTranslator
from textblob import TextBlob
import nltk
import joblib
from datetime import datetime
from urllib.parse import urlparse

# NLTK setup (downloads once)
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# -------------------- Trusted Domains --------------------
TRUSTED_DOMAINS = [
    "linkedin.com", "google.com", "microsoft.com", "apple.com", "amazon.com",
    "paypal.com", "github.com", "irs.gov", "usps.com", "youtube.com"
]

# -------------------- Keywords --------------------
PHISHING_KEYWORDS = [
    "verify", "account", "password", "login", "click here", "suspended", "update",
    "confirm", "urgent", "security alert", "reset your password", "bank", "limited time",
    "verify identity", "suspicious activity", "verify your identity", "failure to act",
    "account locked", "click to claim", "click to update"
]

SOCIAL_ENGINEERING_PHRASES = [
    "can you do me a favor", "urgent but quick", "you’ve been selected",
    "only one who can help", "quick task for you", "talk soon", "grab coffee",
    "hop on a quick call", "need your input asap", "immediate action required",
    "please respond immediately", "time-sensitive", "your immediate attention required", "act now"
]

OBFUSCATION_PATTERNS = [
    r"\bc[1l]ick(?!\s+below)", r"\bacc0unt\b", r"\bl[o0]gin\b", r"\bp[a@]ssword\b", r"\bver[i1]fy\b",
    r"\b[0o]pen\s+[cC]lick\b", r"\b[a1]ctivate\s+your\s+account\b", r"\b[1l]ogin\b",
    r"\b[0o]pen\b", r"\b[a@]ccount\b", r"\b[0o]ffer\b"
]

# -------------------- Logger --------------------
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# -------------------- ML Model: Download & Load --------------------
model_path = "ml_model/phishing_model.pkl"

if not os.path.exists(model_path):
    os.makedirs("ml_model", exist_ok=True)
    print("🔽 Downloading phishing model...")
    try:
        url = "https://drive.google.com/uc?export=download&id=16Cffka8o8-JprSNX4vf40d5u9IXAtIpQ"
        r = requests.get(url)
        with open(model_path, "wb") as f:
            f.write(r.content)
        print("✅ Model downloaded successfully.")
    except Exception as e:
        raise FileNotFoundError(f"❌ Failed to download the model: {e}")

try:
    model = joblib.load(model_path)
except Exception as e:
    raise RuntimeError(f"❌ Failed to load the model: {e}")

# -------------------- ML Detection --------------------
def ml_detect(content):
    try:
        prediction = model.predict([content])[0]
        probability = model.predict_proba([content])[0][1]
        return int(prediction), round(probability * 100, 2)
    except Exception as e:
        logging.error(f"ML detection failed: {e}")
        return 0, 0.0

# -------------------- Rule-Based Detection --------------------
def is_phishing(content):
    logging.info("Scanning email content...")
    content = translate_to_english(content)
    threat_score = 0
    reasons = []
    detected = False
    lower = content.lower()

    for kw in PHISHING_KEYWORDS:
        if kw in lower:
            weight = 2 if kw in ["verify", "login", "password", "reset your password"] else 1
            reasons.append(f"Keyword matched: '{kw}' (weight={weight})")
            threat_score += weight
            detected = True

    for phrase in SOCIAL_ENGINEERING_PHRASES:
        if phrase in lower:
            reasons.append(f"Social engineering phrase: '{phrase}'")
            threat_score += 2
            detected = True

    for pattern in OBFUSCATION_PATTERNS:
        if re.search(pattern, lower):
            reasons.append(f"Obfuscation pattern: '{pattern}'")
            threat_score += 2
            detected = True

    try:
        polarity = TextBlob(content).sentiment.polarity
        if polarity < -0.3:
            reasons.append(f"Negative tone (polarity={polarity:.2f})")
            threat_score += 1
            detected = True
    except Exception as e:
        logging.warning(f"Sentiment analysis failed: {e}")

    try:
        for sentence in nltk.sent_tokenize(content):
            words = nltk.word_tokenize(sentence)
            tags = nltk.pos_tag(words)
            if tags and tags[0][1].startswith("VB"):
                reasons.append(f"Sentence starts with verb: '{sentence[:40]}...'")
                threat_score += 1
                detected = True
    except Exception as e:
        logging.warning(f"POS tagging failed: {e}")

    urls = extract_urls(content)
    for url in urls:
        domain = urlparse(url).netloc
        if any(domain.endswith(t) for t in TRUSTED_DOMAINS):
            reasons.append(f"✅ Trusted domain detected: {domain}")
            threat_score -= 3
        else:
            reasons.append(f"❌ Unrecognized domain: {domain}")
            threat_score += 2
            detected = True

        if len(domain.split(".")) < 2 or any(char.isdigit() for char in domain.split(".")[0]):
            reasons.append(f"❗ Suspicious domain format: {domain}")
            threat_score += 2
            detected = True

    threat_score = max(0, min(threat_score, 10))
    confidence = int((threat_score / 10) * 100)

    if confidence >= 80:
        reasons.append("🚨 High confidence due to multiple strong signals.")
    elif confidence >= 50:
        reasons.append("⚠️ Medium confidence — some red flags present.")
    else:
        reasons.append("ℹ️ Low confidence — mild or uncertain indicators.")

    if confidence < 50:
        detected = False

    return detected, threat_score, confidence, reasons

# -------------------- Helper Functions --------------------
def extract_urls(text):
    return re.findall(r'https?://\S+', text)

def translate_to_english(text):
    try:
        lang = detect(text)
        if lang != "en":
            return GoogleTranslator(source=lang, target="en").translate(text)
    except Exception as e:
        logging.warning(f"Translation failed: {e}")
    return text

def extract_text_from_file(file_path):
    try:
        if file_path.endswith(".txt") or file_path.endswith(".eml"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif file_path.endswith(".msg"):
            import extract_msg
            msg = extract_msg.Message(file_path)
            return msg.body
        elif file_path.endswith(".pdf"):
            import fitz
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text
        else:
            raise ValueError("Unsupported file type")
    except Exception as e:
        logging.warning(f"File extraction failed: {e}")
        return ""

def log_detection_result(content, is_phish, file_name=None):
    os.makedirs("logs", exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    label = "PHISHING" if is_phish else "SAFE"
    with open("logs/detection_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{ts}] - {file_name or 'Console Input'} ➜ {label}\n")
        f.write(f"{content}\n{'-'*60}\n")

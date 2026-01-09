import sys
import logging
from detector import (
    is_phishing,
    extract_text_from_file,
    translate_to_english,
    extract_urls,
    log_detection_result,
    ml_detect  # Importing ML detection function
)

# Logging setup (for terminal output)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

print("=" * 43)
print("     🛡️  AI PHISHING DETECTOR (v1.0)")
print("=" * 43)

# Get input (file or manual)
if len(sys.argv) > 1:
    file_path = sys.argv[1]
    print(f"\n📂 File provided: {file_path}")
    try:
        email_content = extract_text_from_file(file_path)
    except Exception as e:
        print(f"\n❌ Failed to extract email content: {e}")
        sys.exit(1)
else:
    email_content = input("\n📩 Enter the email content to analyze:\n> ")

# Process the email
translated_content = translate_to_english(email_content)

# Rule-based detection
rule_result, score, confidence, reasons = is_phishing(translated_content)

# ML-based detection
ml_result, ml_confidence = ml_detect(translated_content)

# Log results
log_detection_result(translated_content, rule_result)

# Show results
print("\n🧠 **Rule-Based Detection:**")
if rule_result:
    print(f"⚠️ This email is likely a PHISHING attempt based on rule-based analysis.")
    print(f"   Threat Score: {score}/10, Confidence: {confidence}%")
else:
    print(f"✅ This email appears safe based on rule-based analysis.")

print("\n🤖 **ML-Based Detection:**")
if ml_result:
    print(f"⚠️ ML-based prediction: This email is PHISHING.")
    print(f"   Confidence: {ml_confidence}%")
else:
    print(f"✅ ML-based prediction: This email appears SAFE.")
    
# Show reasoning for rule-based detection
print("\n🧠 **Rule-Based Reasoning:**")
for reason in reasons:
    print(f"- {reason}")

# Show URLs found in the email
urls = extract_urls(translated_content)
if urls:
    print("\n🔗 **URLs Found:**")
    for url in urls:
        print(f"- {url}")
else:
    print("\n✅ No URLs found in the email.")

# Final message based on the results
if rule_result or ml_result:
    print("\n⚠️ **ALERT:** This email is likely a phishing attempt.")
else:
    print("\n✅ This email appears safe.")

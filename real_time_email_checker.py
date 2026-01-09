import imaplib
import email
from email.header import decode_header
import time
import schedule
from detector import is_phishing, ml_detect, extract_text_from_file, translate_to_english

# Email server details
IMAP_SERVER = "imap.gmail.com"  # Example for Gmail
IMAP_PORT = 993
EMAIL_ACCOUNT = "your_email@gmail.com"
EMAIL_PASSWORD = "your_password"

# Function to fetch and analyze emails
def fetch_and_analyze_email():
    try:
        # Connect to the email server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)

        # Select the mailbox you want to check (INBOX by default)
        mail.select("inbox")

        # Search for all new emails
        status, messages = mail.search(None, "UNSEEN")  # UNSEEN means unread emails
        email_ids = messages[0].split()

        if email_ids:
            print(f"Found {len(email_ids)} new email(s).")

            for email_id in email_ids:
                # Fetch the email by ID
                status, msg_data = mail.fetch(email_id, "(RFC822)")

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Decode the email subject and sender
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        from_ = msg.get("From")

                        # Print email subject and sender for logging
                        print(f"Subject: {subject}")
                        print(f"From: {from_}")

                        # Get email content
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                # If the email part is text/plain or text/html
                                if "attachment" not in content_disposition:
                                    if content_type == "text/plain":
                                        body = part.get_payload(decode=True).decode()
                                        analyze_email(body)
                                    elif content_type == "text/html":
                                        # You can also process HTML content if needed
                                        pass
                        else:
                            # For non-multipart emails
                            body = msg.get_payload(decode=True).decode()
                            analyze_email(body)

        mail.logout()

    except Exception as e:
        print(f"Error fetching emails: {e}")

# Function to analyze the email content
def analyze_email(content):
    try:
        # Translate content if needed
        translated = translate_to_english(content)

        # Rule-based detection
        detected, score, confidence, reasons = is_phishing(translated)

        # ML-based detection
        ml_result, ml_conf = ml_detect(translated)

        # Log or display the results
        print(f"\n🧠 **Rule-Based Detection:**")
        print(f"Phishing: {detected}, Score: {score}/10, Confidence: {confidence}%")
        print("Reasons:", ", ".join(reasons))

        print(f"\n🤖 **ML-Based Detection:**")
        print(f"Phishing: {'YES' if ml_result else 'NO'}, Confidence: {ml_conf}%")

        if detected or ml_result:
            print("\n⚠️ This email is likely a phishing attempt!")
        else:
            print("\n✅ This email appears safe.")
        
    except Exception as e:
        print(f"Error analyzing email: {e}")

# Schedule the email checking process
schedule.every(5).minutes.do(fetch_and_analyze_email)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)

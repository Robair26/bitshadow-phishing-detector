import imaplib
import email
from email.header import decode_header
import logging
import os  # Ensure this is included
from detector import is_phishing, ml_detect, log_detection_result  # Import the phishing detection functions
import time

# Logging setup (for terminal output)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Email credentials (set via environment variables or a local .env file)
EMAIL_USER = os.getenv('EMAIL_USER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')

if not EMAIL_USER or not EMAIL_PASSWORD:
    raise RuntimeError('Missing EMAIL_USER / EMAIL_PASSWORD. Set them in your environment or create a .env file (see .env.example).')


# Function to check for new emails
def check_for_new_emails():
    try:
        # Create an IMAP4 class with SSL
        mail = imaplib.IMAP4_SSL("imap.gmail.com")

        # Log in to the server
        mail.login(EMAIL_USER, EMAIL_PASSWORD)

        # Select the mailbox you want to check (INBOX is the default)
        mail.select("inbox")

        # Search for unseen emails
        status, messages = mail.search(None, 'UNSEEN')

        # If no emails are found, return immediately
        if status != "OK" or not messages[0]:
            logging.info("No new emails.")
            return

        # Convert the result to a list of email IDs
        email_ids = messages[0].split()

        # Process the most recent email
        latest_email_id = email_ids[-1]
        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                # Get email content
                msg = email.message_from_bytes(response_part[1])

                # Decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else 'utf-8')

                # Decode the sender's email
                from_ = msg.get("From")

                logging.info(f"Subject: {subject}")
                logging.info(f"From: {from_}")

                # Initialize the body as an empty string
                body = ""

                # If the email message is multipart
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        # If the email part is text and not an attachment
                        if "attachment" not in content_disposition:
                            try:
                                # Check if the content is None before attempting to decode
                                payload = part.get_payload(decode=True)
                                if payload:
                                    body = payload.decode()
                                    if body:  # Ensure body is not empty
                                        break
                                    else:
                                        body = "Could not decode body."
                            except Exception as e:
                                logging.error(f"Error decoding part: {e}")
                                body = "Error decoding body."
                else:
                    try:
                        body = msg.get_payload(decode=True).decode()
                    except Exception as e:
                        logging.error(f"Error decoding body: {e}")
                        body = "Could not decode body."

                logging.info(f"Body: {body}")

                # Feed the body content to the phishing detection system
                detected, score, confidence, reasons = is_phishing(body)
                ml_result, ml_conf = ml_detect(body)

                # Log the result
                log_detection_result(body, detected)

                # Display the results
                if detected:
                    logging.warning(f"⚠️ This email is likely a phishing attempt (Score: {score}/10, Confidence: {confidence}%)")
                else:
                    logging.info(f"✅ This email appears safe (Confidence: {confidence}%)")

                logging.info("Rule-based Reasoning:")
                for reason in reasons:
                    logging.info(f"- {reason}")

                logging.info(f"ML Prediction: {'PHISHING' if ml_result else 'SAFE'} (Confidence: {ml_conf}%)")
                logging.info("=" * 60)

        else:
            logging.info("No new emails.")

    except Exception as e:
        logging.error(f"Error checking emails: {e}")

# Function to run the checker periodically (every 10 minutes)
def run_periodically(interval):
    while True:
        check_for_new_emails()
        logging.info(f"Next check in {interval} minutes...")
        time.sleep(interval * 60)  # Wait for the interval (in seconds)

# Run the email checker every 10 minutes
if __name__ == "__main__":
    interval = 10  # Check for new emails every 10 minutes
    run_periodically(interval)
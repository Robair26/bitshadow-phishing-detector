from detector import is_phishing

test_emails = {
    "Safe Email": "Hi Robair, just checking in to see how you’re doing. Talk soon.",
    "Obvious Phishing": "Your account has been suspended! Click here to verify immediately: http://bit.ly/secure-login",
    "Multilingual Phishing": "Votre compte a été suspendu. Cliquez ici pour vérifier: http://bit.ly/verifiez",
    "Tricky Phishing": "Let me know if you’re available to hop on for 10 minutes and I’ll send over the details. Talk soon.",
    "HR Impersonation": "This is the HR department. No need to worry, just update your employee record here."
}

for label, content in test_emails.items():
    result = is_phishing(content)
    status = "PHISHING" if result else "SAFE"
    print(f"[{label}] ➜ {status}")

import extract_msg

def extract_email_body(file_path):
    msg = extract_msg.Message(file_path)
    msg_message = msg.body
    return msg_message

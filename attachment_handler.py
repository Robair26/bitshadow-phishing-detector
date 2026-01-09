import os

def process_attachments(msg):
    attachments = []
    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition"))
        
        if "attachment" in content_disposition:
            filename = part.get_filename()
            content = part.get_payload(decode=True)
            
            # Save attachment to a file
            with open(filename, "wb") as f:
                f.write(content)
                
            attachments.append(filename)
    
    return attachments

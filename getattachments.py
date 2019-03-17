import email
import imaplib
import os
import json

with open("credentials.json") as filename:
    credentials = json.load(filename)


detach_dir = "./attachments" 
user = credentials["email"]
pwd = credentials["password"]

m = imaplib.IMAP4_SSL("imap.gmail.com")
m.login(user, pwd)
m.select("INBOX")

resp, items = m.search(None, "ALL")
items = items[0].split()  

for emailid in items:
    resp, data = m.fetch(emailid, "(RFC822)")
    email_body = data[0][1].decode('utf-8')  
    mail = email.message_from_string(email_body)

    if mail.get_content_maintype() != 'multipart':
        continue

    print ("["+mail["From"]+"] :" + mail["Subject"])

    for part in mail.walk():
        # multipart are just containers, so we skip them
        if part.get_content_maintype() == 'multipart':
            continue

        if part.get('Content-Disposition') is None:
            continue

        filename = part.get_filename()
        att_path = os.path.join(detach_dir,filename)

        if not os.path.isfile(att_path):
            fp = open(att_path, 'wb')
            fp.write(part.get_payload(decode=True))
            fp.close()

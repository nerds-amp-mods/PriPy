import email
from aioimaplib import aioimaplib
import os
import json
import asyncio


@asyncio.coroutine
def get_attachments(host, user, pwd):
    detach_dir = "./attachments" 
    client = aioimaplib.IMAP4_SSL(host=host)

    yield from client.wait_hello_from_server()
    yield from client.login(user, pwd)

    yield from client.select("INBOX")

    yield from client.idle_start(timeout=10)
    while client.has_pending_idle():
        email_event = yield from client.wait_server_push()
        if email_event != "stop_wait_server_push" and "EXISTS" in email_event[0]: 
            emailId = email_event[0].split()[0]
            client.idle_done()

            resp, data = yield from client.fetch(emailId, "(RFC822)")
            mail = email.message_from_bytes(data[1])

            yield from client.idle_start(timeout=10)

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
                if filename is not None:
                    att_path = os.path.join(detach_dir,filename)

                if not os.path.exists(detach_dir):
                    os.mkdir(detach_dir)

                if not os.path.isfile(att_path):
                    fp = open(att_path, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()

if __name__=="__main__":
    host="imap.gmail.com"
    with open("credentials.json") as filename:
        credentials = json.load(filename)
        user = credentials["username"]
        pwd = credentials["password"]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_attachments(host, user, pwd))

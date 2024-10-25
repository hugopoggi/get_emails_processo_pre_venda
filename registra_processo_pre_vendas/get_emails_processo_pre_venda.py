from email.header import decode_header
import json
import imaplib
import email


with open('config.json', 'r') as config_file:
    config = json.load(config_file)

username = config['username']
password = config['password']

imap_server = 'imap.gmail.com'
mail = imaplib.IMAP4_SSL(imap_server)

mail.login(username,password)

mail.select('inbox')

status, messages = mail.search(None,'SEEN')
email_ids = messages[0].split()
emails_dados = []

if not email_ids:
    print('Nenhum e-mail não lido encontrado.')
else:
    for emails in email_ids:
        status, msg_data = mail.fetch(emails, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else 'utf=8')

                from_ = msg.get('From')

                cc = msg.get('Cc')
                cc_addresses = cc.split(',') if cc else []
                body = ''
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get('Content-Disposition'))

                        if content_type == 'text/plain' and 'attachment' not in content_disposition:
                            body = part.get_payload(decode=True).decode()
                            break

                else:
                    body = msg.get_payload(decode=True).decode()

                email_data ={
                    "Assunto": subject,
                    "PessoaEmail": from_,
                    "PessoaEmailComCopia": [addr.strip() for addr in cc_addresses],
                    "ProcessoComentario": body
                }

                emails_dados.append(email_data)

mail.logout()

json_data = json.dumps(emails_dados, indent=4, ensure_ascii=False)
print(json_data)
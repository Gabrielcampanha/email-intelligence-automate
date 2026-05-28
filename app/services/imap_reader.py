import imaplib
import email
from email.header import decode_header
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

def get_real_emails() -> List[Dict[str, Any]]:
    """
    Conecta ao servidor IMAP e busca e-mails não lidos.
    """
    imap_server = os.getenv("IMAP_SERVER")
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    # Se as credenciais não estiverem configuradas ou forem o padrão, retorna lista vazia
    if not all([imap_server, email_user, email_pass]) or email_user == "seu-email@gmail.com":
        return []

    emails_list = []
    try:
        # Conexão segura com o servidor IMAP
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select("inbox")

        # Busca apenas e-mails não lidos (UNSEEN)
        status, messages = mail.search(None, 'UNSEEN')
        
        if status != 'OK':
            return []

        # Processa os IDs dos e-mails encontrados
        for num in messages[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            if status != 'OK':
                continue

            for response_part in data:
                if isinstance(response_part, tuple):
                    # Transforma os bytes do e-mail em um objeto message
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decodifica o assunto do e-mail
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    # Extrai o remetente
                    from_ = msg.get("From")
                    
                    # Extrai o corpo do e-mail (priorizando texto puro)
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()

                    emails_list.append({
                        "id": f"real_{num.decode()}",
                        "from": from_,
                        "subject": subject,
                        "body": body
                    })

        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"Erro ao acessar servidor IMAP: {e}")
    
    return emails_list

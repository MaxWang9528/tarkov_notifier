from os.path import basename
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import smtplib
import ssl
import info


def send_sms(number, message, provider, credentials, subject='', smtp_server='smtp.gmail.com', smtp_port=465):
    sender_email = credentials[0]
    email_password = credentials[1]
    receiver_email = f'{number}@{info.PROVIDERS.get(provider).get("sms")}'

    email_message = f'Subject:{subject}\nTo:{receiver_email}\n{message}'

    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=ssl.create_default_context()) as email:
        email.login(sender_email, email_password)
        email.sendmail(sender_email, receiver_email, email_message)


def send_mms(number, message, at, credentials, file_path, mime_maintype, mime_subtype,
             subject='', smtp_server='smtp.gmail.com', smtp_port=465):
    sender_email = credentials[0]
    email_password = credentials[1]
    receiver_email = f'{number}@{at}'

    # form message
    email_message = MIMEMultipart()
    email_message['subject'] = subject
    email_message['to'] = receiver_email
    email_message['from'] = sender_email
    email_message.attach(MIMEText(message, 'plain'))

    # attach file
    with open(file_path, 'rb') as attachment:
        part = MIMEBase(mime_maintype, mime_subtype)
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={basename(file_path)}')

        email_message.attach(part)

    text = email_message.as_string()

    # auth and send
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=ssl.create_default_context()) as email:
        email.login(sender_email, email_password)
        email.sendmail(sender_email, receiver_email, text)

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(
    port=587,
    smtp_server="mailhub1.gmail.com",
    sender_email="john.doe@gmail.com",
    receiver_email=["j.doe@gmail.com"],
    subject="Sujet test auto",
    body="This message is sent from app.",
):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    text = message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, "app_password")
        server.sendmail(sender_email, receiver_email, text)

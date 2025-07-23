import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

def send_email(subject, body, to_email, smtp_user, smtp_pass, smtp_server, smtp_port, attachment_path=None, logger=None):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to_email

        msg.attach(MIMEText(body, 'plain'))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                file_part = MIMEApplication(f.read(), _subtype="pdf")
                file_part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                msg.attach(file_part)
            if logger: logger.info(f"Attached file: {attachment_path}")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        if logger: logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        if logger: logger.error(f"Failed to send email: {e}")
        return False

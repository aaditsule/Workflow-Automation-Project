import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, to_email, smtp_user, smtp_pass, smtp_server, smtp_port, logger=None):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        log_msg = f"Email sent to {to_email}"
        if logger: logger.info(log_msg)
        else: print(log_msg)

        return True
    except Exception as e:
        error_msg = f"Failed to send email to {to_email}: {e}"
        if logger: logger.error(error_msg)
        else: print(error_msg)
        return False

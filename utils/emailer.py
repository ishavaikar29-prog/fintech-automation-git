import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from .utils import retry
from .error_handler import log_exception, log_info

@retry(tries=3, delay=2, backoff=2, allowed_exceptions=(Exception,), logger=None)
def send_email_with_attachments(smtp_host, smtp_port, smtp_user, smtp_pass, to_email, subject, body, attachments):
    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        for fpath in attachments:
            if not fpath or not os.path.exists(fpath):
                continue
            part = MIMEBase("application", "octet-stream")
            with open(fpath, "rb") as f:
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(fpath)}"')
            msg.attach(part)

        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        log_info("Email sent successfully")
    except Exception as e:
        log_exception("EMAIL SEND FAILED", e)
        raise

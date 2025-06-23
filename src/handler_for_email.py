import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional

def send_email_message(
    hostname: str,
    port: Optional[int],
    username: str,
    password: str,
    mail: EmailMessage,
    log=None,
    use_ssl: bool = False,
    ignore_certificate_errors: bool = False
):
    """
    Send an EmailMessage via SMTP.

    :param hostname:      SMTP server host
    :param port:          SMTP port (e.g. 25, 587, 465)
    :param username:      SMTP username
    :param password:      SMTP password
    :param mail:          email.message.EmailMessage instance, pre‐populated
    :param log:           
    :param use_ssl:       if True, connect via smtplib.SMTP_SSL; otherwise start TLS
    :param ignore_certificate_errors: if True, skip SSL cert verification
    """

    # collect recipients for logging
    recipients = mail.get_all('to', []) + mail.get_all('cc', []) + mail.get_all('bcc', [])
    recipients_str = ", ".join(recipients)

    # optionally build an SSL context
    context = None
    if use_ssl or ignore_certificate_errors:
        context = ssl.create_default_context()
        if ignore_certificate_errors:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

    # connect to SMTP
    if use_ssl:
        smtp = smtplib.SMTP_SSL(hostname, port or 465, context=context)
    else:
        smtp = smtplib.SMTP(hostname, port or 587)

    try:
        smtp.ehlo()
        if not use_ssl:
            # upgrade to TLS if the server supports it
            smtp.starttls(context=context)
            smtp.ehlo()

        # login
        smtp.login(username, password)

        smtp.send_message(mail)

    finally:
        smtp.quit()
        
def send_email(
    hostname: str,
    port: Optional[int],
    username: str,
    password: str,
    from_address: str,
    to_address: str,
    subject: str,
    body: str,
    body_is_html: bool = False,
    log=None,
    use_ssl: bool = False,
    ignore_certificate_errors: bool = False
):
    # build your EmailMessage
    msg = EmailMessage()
    msg["From"] = from_address
    msg["To"] = to_address
    msg["Subject"] = subject
    if body_is_html:        
        msg.set_content(body)
        msg.add_alternative(body, subtype="html")
    else:
        msg.set_content(body)

    # send it
    send_email_message(
        hostname,
        port,
        username,
        password,
        msg,
        log,
        use_ssl,
        ignore_certificate_errors
    )

# -------------------------
# Example usage:
if __name__ == "__main__":   
    send_email(
        hostname="mail.f4cio.com",
        port=465,
        username="t@f4cio.com",
        password="4444.t.4444",
        from_address="t@f4cio.com",
        to_address="f4cio@f4cio.com",
        subject="Test Email",
        body="<p>This is the <b>HTML</b> body.</p>",
        body_is_html=True,
        log=None,
        use_ssl=False,
        ignore_certificate_errors=False
    )



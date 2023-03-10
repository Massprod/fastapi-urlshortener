import os
import smtplib
import requests
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta


def working_url(url: str, timeout: int = 4) -> bool:
    try:
        if requests.head(url, timeout=timeout).status_code < 400:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False


def expire_date(days: int = 7, seconds: int = 0) -> datetime:
    now = datetime.utcnow()
    expire = now + timedelta(days=days, seconds=seconds)
    return expire


def create_rshort(length: int = 3) -> str:
    if length <= 2 or length >= 11:
        raise AttributeError("Length should be from 3 to 10")
    short = "".join(random.choices(string.ascii_letters + string.digits, k=length))
    return short


def create_send_key(receiver: str, link: str, api_key: str) -> bool:
    try:
        email = os.getenv("EMAIL")
        email_key = os.getenv("EMAIL_KEY")
        msg = MIMEMultipart("alternative")

        html_part = f"""
                        <html>
                        <head></head>
                            <body>
                                <p>Click on <a href={link}>THIS</a> to activate you api-key: <b>{api_key}</b></p>
                            </body>
                        </html>
                    """

        html_part = MIMEText(html_part, "html")
        msg["Subject"] = "Shorty api-key"
        msg.attach(html_part)
        msg = msg.as_string()

        con = smtplib.SMTP("smtp.gmail.com")
        con.starttls()
        con.login(user=email,
                  password=email_key
                  )
        con.sendmail(from_addr=email,
                     to_addrs=receiver,
                     msg=msg
                     )
        con.close()
        return True
    except smtplib.SMTPException:
        return False

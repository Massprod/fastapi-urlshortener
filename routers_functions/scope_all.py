import os
import smtplib
import requests
import random
import string
from datetime import datetime, timedelta

import sqlalchemy.exc
from sqlalchemy.orm import Session

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from database.models import *


def working_url(url: str, timeout: int = 4) -> bool:
    """Checking given Url for response. Return True if status code < 400. False otherwise"""
    try:
        if requests.head(url, timeout=timeout).status_code < 400:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False


def expire_date(days: int = 7, seconds: int = 0) -> datetime:
    """Creating DATETIME object with given Days, Seconds offset"""
    now = datetime.utcnow()
    expire = now + timedelta(days=days, seconds=seconds)
    return expire


def create_rshort(length: int = 3) -> str:
    """Creating Random string with given Length - limit 3 to 10"""
    if not 2 < length < 11:
        raise AttributeError("Length should be from 3 to 10")
    short = "".join(random.choices(string.ascii_letters + string.digits, k=length))
    return short


def create_send_key(receiver: str, link: str, api_key: str) -> bool:
    """Creates and sends Email with activation link in it"""
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


def del_expired(db_model: Base, db: Session, email: str = None,
                username: str = None, del_one_short: str = None, delete_all: bool = False) -> None | bool:
    """Deleting expired records from Db with given Table.
    Returns True if expired record deleted,
    False if record exist and not expired,
    None if record not found."""
    if delete_all:
        try:
            all_exp_data = db.query(db_model).with_entities(db_model.expire_date).all()
            all_exp_data = [_[0] for _ in all_exp_data if _[0] is not None]
            for _ in all_exp_data:
                if _ <= datetime.utcnow():
                    to_delete = db.query(db_model).filter_by(expire_date=_).all()
                    for _ in to_delete:
                        db.delete(_)
            db.commit()
            return True
        except AttributeError:
            return None
    elif email:
        try:
            exp_data = db.query(db_model).filter_by(email=email).first()
            if exp_data.expire_date <= datetime.utcnow():
                db.delete(exp_data)
                db.commit()
                return True
            return False
        except AttributeError:
            return None
    elif username:
        try:
            exp_data = db.query(db_model).filter_by(username=username).first()
            if exp_data.expire_date <= datetime.utcnow():
                db.delete(exp_data)
                db.commit()
                return True
            return False
        except AttributeError:
            return None
    elif del_one_short:
        try:
            exp_data = db.query(db_model).filter_by(short_url=del_one_short).first()
            if exp_data.expire_date <= datetime.utcnow():
                db.delete(exp_data)
                db.commit()
                return True
            return False
        except AttributeError:
            return None

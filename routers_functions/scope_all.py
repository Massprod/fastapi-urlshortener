from __future__ import annotations  # to use None | bool at del_expire()[88line] with python3.9 or less
import os
import smtplib
import requests
import random
import string
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from database.models import Base


def working_url(url: str, timeout: int = 3) -> bool:
    """Checking given Url for response. Return True if status code < 400. False otherwise"""
    try:
        if requests.head(url, timeout=timeout).status_code < 400:
            return True
        return False
    # there's too many exceptions to cover, as we generally care for working urls with 200, 302
    # Ignore all Exceptions for now or I can create MockServer...imo not worth in this case
    except requests.exceptions.RequestException:
        return False


def expire_date(days: int = 7, seconds: int = 0) -> datetime:
    """Creating DATETIME object with given Days, Seconds offset"""
    now = datetime.utcnow()
    expire = now + timedelta(days=days, seconds=seconds)
    return expire


def create_rshort(length: int = 3) -> str:
    """Creating Random string with given Length - limit 1 to 10"""
    if not 0 < length < 11:
        raise AttributeError("Length should be from 1 to 10")
    short = "".join(random.choices(string.ascii_letters + string.digits, k=length))
    return short


def create_send_key(receiver: str, link: str, api_key: str) -> bool:
    """Creates and sends Email with activation link in it"""
    email = os.getenv("EMAIL")
    email_key = os.getenv("EMAIL_KEY")
    if email is None or email_key is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="ENV variables: EMAIL, EMAIL_KEY  can't be empty. "
                                   "Check if you're set ENV correctly")
    try:
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
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"{email}\n\nEmail sender not Authenticated. Set correct ENV")
    except smtplib.SMTPException:
        return False


def del_expired(db_model: Base, db: Session, email: str = None,
                username: str = None, del_one_short: str = None, delete_all: bool = False) -> None | bool:
    """Deleting expired records from Db with given Table.
    Returns True if expired record deleted,
    False if record exist and not expired,
    None if record not found."""
    if delete_all:
        if all_exp_data := db.query(db_model).with_entities(db_model.expire_date).all():
            all_exp_data = [_[0] for _ in all_exp_data if _[0] is not None]
            for _ in all_exp_data:
                if _ <= datetime.utcnow():
                    to_delete = db.query(db_model).filter_by(expire_date=_).all()
                    for _ in to_delete:
                        db.delete(_)
            db.commit()
            return True
    elif email:
        if exp_data := db.query(db_model).filter_by(email=email).first():
            if exp_data.expire_date is None:
                return False
            elif exp_data.expire_date <= datetime.utcnow():
                db.delete(exp_data)
                db.commit()
                return True
            return False
        return None
    elif username:
        if exp_data := db.query(db_model).filter_by(username=username).first():
            if exp_data.expire_date is None:
                return False
            elif exp_data.expire_date <= datetime.utcnow():
                db.delete(exp_data)
                db.commit()
                return True
            return False
        return None
    elif del_one_short:
        if exp_data := db.query(db_model).filter_by(short_url=del_one_short).first():
            if exp_data.expire_date <= datetime.utcnow():
                db.delete(exp_data)
                db.commit()
                return True
            return False


def check_records_count(db: Session, db_model: Base, length: int):
    """Count number of records in Db for given length"""
    records_count = db.query(db_model).filter_by(length=length).count()
    return records_count

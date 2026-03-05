import logging
import os
from dataclasses import dataclass
from typing import Protocol, Dict, List

import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
import smtplib

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Settings:
    event_id: str
    event_name: str
    url: str
    target_date: str
    email_to: List[str]
    email_from: str
    smtp_server: str
    smtp_user: str
    smtp_password: str

    @classmethod
    def from_env(cls) -> "Settings":
        env = os.environ
        required = [
            "EVENT_ID",
            "EVENT_NAME",
            "URL",
            "TARGET_DATE",
            "EMAIL_TO",
            "EMAIL_FROM",
            "SMTP_SERVER",
            "SMTP_USER",
            "SMTP_PASSWORD",
        ]
        missing = [k for k in required if not env.get(k)]
        if missing:
            raise RuntimeError(f"missing env vars: {', '.join(missing)}")
        return cls(
            event_id=env["EVENT_ID"],
            event_name=env["EVENT_NAME"],
            url=env["URL"],
            target_date=env["TARGET_DATE"].upper(),
            email_to=[e.strip() for e in env["EMAIL_TO"].split(",") if e.strip()],
            email_from=env["EMAIL_FROM"],
            smtp_server=env["SMTP_SERVER"],
            smtp_user=env["SMTP_USER"],
            smtp_password=env["SMTP_PASSWORD"],
        )


class Checker(Protocol):
    def check(self, html: str, target_date: str) -> bool:
        ...


class SDGChecker:
    def check(self, html: str, target_date: str) -> bool:
        soup = BeautifulSoup(html, "html.parser")
        for div in soup.find_all("div", class_="el-meta"):
            if target_date == div.get_text(strip=True).upper():
                return True
        return False


class FigaroChecker:
    def check(self, html: str, target_date: str) -> bool:
        soup = BeautifulSoup(html, "html.parser")
        time_tag = soup.find(
            "time",
            attrs={"datetime": lambda d: d and d.startswith(target_date)}
        )
        if not time_tag:
            return False
        row = time_tag.find_parent("tr")
        link = row.find("a", href=lambda h: h and "koobin.com" in h)
        return bool(link)


CHECKERS: Dict[str, Checker] = {
    "SDG": SDGChecker(),
    "FIGARO": FigaroChecker(),
}


def fetch_page(url: str, timeout: int = 30) -> str:
    logger.debug("fetching %s", url)
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def send_email(settings: Settings) -> None:
    msg = EmailMessage()
    msg["Subject"] = f"{settings.event_name} xa dispoñible!"
    msg["From"] = settings.email_from
    msg["To"] = ", ".join(settings.email_to)
    msg.set_content(
        f"Xa están dispoñibles as entradas para o {settings.target_date} de "
        f"{settings.event_name}.\n\nCorre que voan:\n{settings.url}"
    )
    logger.debug("sending mail to %s", settings.email_to)
    with smtplib.SMTP_SSL(settings.smtp_server, 465) as srv:
        srv.login(settings.smtp_user, settings.smtp_password)
        srv.send_message(msg)


def check_and_alert(settings: Settings) -> bool:
    checker = CHECKERS.get(settings.event_id)
    if checker is None:
        raise ValueError(f"unknown event: {settings.event_id}")
    html = fetch_page(settings.url)
    available = checker.check(html, settings.target_date)
    if available:
        logger.info("tickets found, sending message")
        send_email(settings)
    else:
        logger.info("no tickets yet")
    print(f"tickets_found={'true' if available else 'false'}")
    return available


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = Settings.from_env()
    check_and_alert(settings)

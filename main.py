import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import os

event_id = os.getenv("EVENT_ID")
url = os.getenv("URL")
target_date = os.getenv("TARGET_DATE")
email_to = os.getenv("EMAIL_TO")
event_name = os.getenv("EVENT_NAME")

def send_email():
    msg = EmailMessage()
    msg["Subject"] = f"{event_name} xa dispoñible!"
    msg["From"] = os.environ["EMAIL_FROM"]

    recipients = [email.strip() for email in email_to.split(",")]
    msg["To"] = ", ".join(recipients)

    msg.set_content(
        f"Xa están dispoñibles as entradas para o {target_date} de {event_name}.\n\n"
        f"Corre que voan:\n{url}"
    )

    with smtplib.SMTP_SSL(os.environ["SMTP_SERVER"], 465) as server:
        server.login(
            os.environ["SMTP_USER"],
            os.environ["SMTP_PASSWORD"]
        )
        server.send_message(msg)

def main_SDG():
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    date_divs = soup.find_all("div", class_="el-meta")

    for div in date_divs:
        if target_date == div.get_text(strip=True).upper():
            print("Tickets found! Sending email.")
            send_email()
            print("tickets_found=true")
            return

    print("Tickets not available yet.")
    print("tickets_found=false")

def main_Figaro():
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    time_tag = soup.find(
        "time",
        attrs={"datetime": lambda d: d and d.startswith(target_date)}
    )

    if not time_tag:
        print("Tickets not available yet.")
        print("tickets_found=false")
        return

    row = time_tag.find_parent("tr")

    link = row.find("a", href=lambda h: h and "koobin.com" in h)

    if link:
        print("Tickets found! Sending email.")
        send_email()
        print("tickets_found=true")
    else:
        print("Tickets not available yet.")
        print("tickets_found=false")

if __name__ == "__main__":
    if event_id == "SDG":
        main_SDG()
    elif event_id == "FIGARO":
        main_Figaro()
    else:
        raise ValueError(f"Unknown EVENT_ID: {event_id}")
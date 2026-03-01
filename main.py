import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

event_id = os.getenv("EVENT_ID")

def send_email(event_id):
    event_name = os.environ[f"EVENT_NAME_{event_id}"]
    email_to = os.environ[f"EMAIL_TO_{event_id}"]
    url = os.environ[f"URL_{event_id}"]
    target_date = os.environ[f"TARGET_DATE_{event_id}"]

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

def main_SDG(event_id):
    url = os.environ[f"URL_{event_id}"]
    target_date = os.environ[f"TARGET_DATE_{event_id}"]

    r = requests.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    date_divs = soup.find_all("div", class_="el-meta")
    for div in date_divs:
        date_text = div.get_text(strip=True).upper()
        if target_date == date_text:
            print("Tickets found! Sending email.")
            send_email(event_id)
            print(f"tickets_found_{event_id}=true")
            return
    
    print("Tickets not available yet.")
    print(f"tickets_found_{event_id}=false")

def main_Figaro(event_id):
    url = os.environ[f"URL_{event_id}"]
    target_date = os.environ[f"TARGET_DATE_{event_id}"]

    r = requests.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Find the row containing the target date
    time_tag = soup.find(
        "time",
        attrs={"datetime": lambda d: d and d.startswith(target_date)}
    )
    if not time_tag:
        print("Target date row not found.")
        return
    
    row = time_tag.find_parent("tr")

    # Check for Koobin link
    link = row.find("a", href=lambda h: h and "koobin.com" in h)
    if link:
        print("Tickets found! Sending email.")
        send_email(event_id)
        print(f"tickets_found_{event_id}=true")
    else:
        print("Tickets not available yet.")
        print(f"tickets_found_{event_id}=false")

if __name__ == "__main__":
    if event_id == "SDG":
        main_SDG(event_id)
    elif event_id == "FIGARO":
        main_Figaro(event_id)
    else:
        raise ValueError(f"Unknown EVENT_ID: {event_id}")
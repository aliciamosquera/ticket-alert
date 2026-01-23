import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

URL = os.environ["URL"]
TARGET_DATE = os.environ["TARGET_DATE"]

def send_email():
    msg = EmailMessage()
    msg["Subject"] = "Le Nozze di Figaro xa está dispoñible!"
    msg["From"] = os.environ["EMAIL_FROM"]
    recipients = [email.strip() for email in os.environ["EMAIL_TO"].split(",")]
    msg["To"] = ", ".join(recipients)

    msg.set_content(
        f"Xa está dispoñible a sesión Under35 para 'Le Nozze di Figaro'.\n\n"
        f"Corre que voa:\n{URL}"
    )

    with smtplib.SMTP_SSL(os.environ["SMTP_SERVER"], 465) as server:
        server.login(
            os.environ["SMTP_USER"],
            os.environ["SMTP_PASSWORD"]
        )
        server.send_message(msg)

def main():
    r = requests.get(URL, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # Find the row containing the target date
    time_tag = soup.find(
        "time",
        attrs={"datetime": lambda d: d and d.startswith(TARGET_DATE)}
    )
    if not time_tag:
        print("Target date row not found.")
        return

    row = time_tag.find_parent("tr")

    # Check for Koobin link
    link = row.find("a", href=lambda h: h and "koobin.com" in h)
    if link:
        print("Tickets found! Sending email.")
        send_email()
        print("tickets_found=true")
    else:
        print("Tickets not available yet.")
        print("tickets_found=false")

if __name__ == "__main__":
    main()
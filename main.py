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
    msg["Subject"] = "Sanguijuelas del Guadiana ya disponibles!"
    msg["From"] = os.environ["EMAIL_FROM"]
    recipients = [email.strip() for email in os.environ["EMAIL_TO"].split(",")]
    msg["To"] = ", ".join(recipients)

    msg.set_content(
        f"Ya están disponibles las entradas para el 8 de septiembre de Las Sanguijuelas del Guadiana.\n\n"
        f"Corre que vuelan:\n{URL}"
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

    # Find all date divs
    date_divs = soup.find_all("div", class_="el-meta")

    for div in date_divs:
        date_text = div.get_text(strip=True).upper()
        if TARGET_DATE == date_text:
            print("Tickets found! Sending email.")
            send_email()
            print("tickets_found=true")
            return
    
    print("Tickets not available yet.")
    print("tickets_found=false")

if __name__ == "__main__":
    main()
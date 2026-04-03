from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import csv
import os
import requests

app = FastAPI()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
csv_file = "leads.csv"

if not os.path.exists(csv_file):
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Email", "Phone", "Company"])


def send_email(name, email, phone, company):
    if not RESEND_API_KEY:
        return

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "from": "onboarding@resend.dev",
        "to": ["mailtomemohan94@gmail.com"],
        "subject": "New Demo Request",
        "html": f"<h3>{name} - {email} - {phone} - {company}</h3>"
    }

    try:
        requests.post(url, json=data, headers=headers, timeout=10)
    except:
        pass


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>Demo Request Form</h2>
    <form action="/submit" method="post">
        Name: <input name="name"><br><br>
        Email: <input name="email"><br><br>
        Phone: <input name="phone"><br><br>
        Company: <input name="company"><br><br>
        <button type="submit">Submit</button>
    </form>
    """


@app.post("/submit", response_class=HTMLResponse)
def submit(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    company: str = Form("")
):
    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([name, email, phone, company])

    send_email(name, email, phone, company)

    return f"<h2>Success {name}</h2>"

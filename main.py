from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import csv
import os
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
csv_file = "leads.csv"

if not os.path.exists(csv_file):
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Email", "Phone", "Company"])


def send_email(name, email, phone, company):
    if not RESEND_API_KEY:
        print("RESEND_API_KEY not set")
        return

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    admin_data = {
        "from": "onboarding@resend.dev",
        "to": ["mailtomemohan94@gmail.com"],
        "subject": "New Demo Request",
        "html": f"""
        <h2>New Demo Request</h2>
        <p><b>Name:</b> {name}</p>
        <p><b>Email:</b> {email}</p>
        <p><b>Phone:</b> {phone}</p>
        <p><b>Company:</b> {company}</p>
        """
    }

    user_data = {
        "from": "onboarding@resend.dev",
        "to": [email],
        "subject": "Thanks for contacting us",
        "html": f"""
        <h2>Thanks for contacting us</h2>
        <p>Hi {name},</p>
        <p>Thanks for your interest.</p>
        <p>We have received your demo request.</p>
        <p>Our team will contact you shortly.</p>
        <p>Regards,<br>Mohan</p>
        """
    }

    try:
        requests.post(url, json=admin_data, headers=headers, timeout=20)
        requests.post(url, json=user_data, headers=headers, timeout=20)
        print("Both emails sent successfully")
    except Exception as e:
        print("Email error:", e)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/submit", response_class=HTMLResponse)
def submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    company: str = Form("")
):
    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([name, email, phone, company])

    send_email(name, email, phone, company)

    return f"""
    <html>
        <head>
            <title>Success</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 700px;
                    margin: 40px auto;
                    padding: 20px;
                    line-height: 1.6;
                }}
                .box {{
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    padding: 20px;
                }}
                a {{
                    display: inline-block;
                    margin-top: 15px;
                    text-decoration: none;
                    background: #4CAF50;
                    color: white;
                    padding: 10px 16px;
                    border-radius: 6px;
                }}
            </style>
        </head>
        <body>
            <div class="box">
                <h2>Saved Successfully</h2>
                <p><b>Name:</b> {name}</p>
                <p><b>Email:</b> {email}</p>
                <p><b>Phone:</b> {phone}</p>
                <p><b>Company:</b> {company}</p>
                <p>We will contact you soon.</p>
                <a href="/">Back to Form</a>
            </div>
        </body>
    </html>
    """

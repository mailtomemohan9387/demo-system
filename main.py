from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import os
import csv
import requests

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/images", StaticFiles(directory="images"), name="images")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
csv_file = "leads.csv"

# leads.csv create if not exists
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

    # Admin email
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

    # User confirmation email
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
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/form", response_class=HTMLResponse)
def form_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.get("/submit", response_class=HTMLResponse)
def prevent_direct_submit():
    return """
    <html>
        <head>
            <title>Invalid Access</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 40px;
                }
                a {
                    display: inline-block;
                    margin-top: 20px;
                    text-decoration: none;
                    background: #4CAF50;
                    color: white;
                    padding: 10px 18px;
                    border-radius: 6px;
                }
            </style>
        </head>
        <body>
            <h2>Please submit the form properly</h2>
            <a href="/">Back to Home</a>
        </body>
    </html>
    """


@app.post("/submit", response_class=HTMLResponse)
def submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    company: str = Form("")
):
    # Save to CSV
    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([name, email, phone, company])

    # Send emails
    send_email(name, email, phone, company)

    return f"""
    <html>
        <head>
            <title>Success</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #f9f9f9;
                    margin: 0;
                    padding: 40px;
                }}
                .box {{
                    max-width: 700px;
                    margin: auto;
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 12px;
                    padding: 25px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    line-height: 1.8;
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
                <a href="/">Back to Home</a>
            </div>
        </body>
    </html>
    """

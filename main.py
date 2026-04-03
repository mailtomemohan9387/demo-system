from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import csv
import os
import requests
import uuid
from datetime import datetime, timedelta

app = FastAPI()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

LEADS_FILE = "leads.csv"
DEMO_FILE = "demo_links.csv"

if not os.path.exists(LEADS_FILE):
    with open(LEADS_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Email", "Phone", "Company"])

if not os.path.exists(DEMO_FILE):
    with open(DEMO_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Email", "Token", "Expiry"])


def send_email(to_email, subject, html_body):
    if not RESEND_API_KEY:
        print("RESEND_API_KEY not set")
        return

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "from": "onboarding@resend.dev",
        "to": [to_email],
        "subject": subject,
        "html": html_body
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=15)
        print("Mail status:", response.status_code)
        print("Mail response:", response.text)
    except Exception as e:
        print("Mail error:", e)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Demo Request Form</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f5f7fb;
                margin: 0;
                padding: 20px;
            }
            .box {
                max-width: 700px;
                margin: 40px auto;
                background: white;
                border-radius: 14px;
                box-shadow: 0 4px 18px rgba(0,0,0,0.08);
                padding: 30px;
            }
            h2 {
                margin-top: 0;
                color: #222;
            }
            p {
                color: #666;
            }
            label {
                font-weight: bold;
                display: block;
                margin-top: 15px;
                margin-bottom: 6px;
                color: #333;
            }
            input {
                width: 100%;
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 8px;
                box-sizing: border-box;
                font-size: 15px;
            }
            button {
                margin-top: 20px;
                background: #28a745;
                color: white;
                border: none;
                padding: 12px 22px;
                border-radius: 8px;
                font-size: 15px;
                cursor: pointer;
            }
            button:hover {
                background: #218838;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Demo Request Form</h2>
            <p>Please enter your details below.</p>

            <form action="/submit" method="post">
                <label>Name</label>
                <input name="name" required>

                <label>Email</label>
                <input name="email" type="email" required>

                <label>Phone</label>
                <input name="phone" required>

                <label>Company</label>
                <input name="company">

                <button type="submit">Submit</button>
            </form>
        </div>
    </body>
    </html>
    """


@app.post("/submit", response_class=HTMLResponse)
def submit(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    company: str = Form("")
):
    now = datetime.now()

    # Save lead
    with open(LEADS_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name, email, phone, company])

    # Generate token
    token = str(uuid.uuid4())
    expiry = now + timedelta(hours=1)

    # Save demo token
    with open(DEMO_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([email, token, expiry.isoformat()])

    demo_link = f"https://demo-system-9qv6.onrender.com/demo/{token}"

    # Admin mail
    send_email(
        "mailtomemohan94@gmail.com",
        "New Demo Request",
        f"""
        <div style="font-family:Arial,sans-serif;line-height:1.6">
            <h2>New Demo Request</h2>
            <p><b>Name:</b> {name}</p>
            <p><b>Email:</b> {email}</p>
            <p><b>Phone:</b> {phone}</p>
            <p><b>Company:</b> {company}</p>
        </div>
        """
    )

    # User confirmation mail
    send_email(
        email,
        "Thanks for contacting us",
        f"""
        <div style="font-family:Arial,sans-serif;line-height:1.6">
            <h2>Thanks for contacting us</h2>
            <p>Hi {name},</p>
            <p>Thanks for your interest.</p>
            <p>We have received your demo request successfully.</p>
            <p>Our team will contact you shortly.</p>
            <p>Regards,<br>Mohan</p>
        </div>
        """
    )

    # Demo link mail
    send_email(
        email,
        "Your Demo Access Link (Valid for 1 Hour)",
        f"""
        <div style="font-family:Arial,sans-serif;line-height:1.6">
            <h2>Your Demo Access Link</h2>
            <p>Your demo link is ready.</p>
            <p>This link is valid for <b>1 hour only</b>.</p>
            <p>
                <a href="{demo_link}" style="display:inline-block;padding:10px 16px;background:#28a745;color:white;text-decoration:none;border-radius:6px;">
                    Open Demo
                </a>
            </p>
            <p>Or copy this link:</p>
            <p>{demo_link}</p>
        </div>
        """
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Success</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f7fb;
                margin: 0;
                padding: 20px;
            }}
            .box {{
                max-width: 700px;
                margin: 40px auto;
                background: white;
                border-radius: 14px;
                box-shadow: 0 4px 18px rgba(0,0,0,0.08);
                padding: 30px;
                line-height: 1.8;
            }}
            h2 {{
                color: #222;
                margin-top: 0;
            }}
            p {{
                color: #444;
            }}
            a {{
                display: inline-block;
                margin-top: 20px;
                text-decoration: none;
                background: #28a745;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
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


@app.get("/demo/{token}", response_class=HTMLResponse)
def demo(token: str):
    valid = False
    matched_email = ""

    with open(DEMO_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)

        for row in reader:
            if len(row) < 3:
                continue

            saved_email = row[0]
            saved_token = row[1]
            saved_expiry = row[2]

            if saved_token == token:
                matched_email = saved_email
                expiry_time = datetime.fromisoformat(saved_expiry)

                if datetime.now() < expiry_time:
                    valid = True
                break

    if not valid:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Link Expired</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f5f7fb;
                    margin: 0;
                    padding: 20px;
                }
                .box {
                    max-width: 700px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 14px;
                    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
                    padding: 30px;
                    line-height: 1.8;
                }
                a {
                    display: inline-block;
                    margin-top: 20px;
                    text-decoration: none;
                    background: #dc3545;
                    color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                }
            </style>
        </head>
        <body>
            <div class="box">
                <h2>Link expired or invalid</h2>
                <p>Please request a new demo link.</p>
                <a href="/">Request Again</a>
            </div>
        </body>
        </html>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Demo Access</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f7fb;
                margin: 0;
                padding: 20px;
            }}
            .box {{
                max-width: 800px;
                margin: 40px auto;
                background: white;
                border-radius: 14px;
                box-shadow: 0 4px 18px rgba(0,0,0,0.08);
                padding: 30px;
                line-height: 1.8;
            }}
            .warn {{
                color: red;
                font-weight: bold;
            }}
            ul {{
                padding-left: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Demo Access (Read Only)</h2>
            <p>Welcome, <b>{matched_email}</b></p>
            <p>This demo link is valid for 1 hour only.</p>

            <ul>
                <li>Customer: Demo User</li>
                <li>Invoice: ₹1000</li>
                <li>Status: Paid</li>
                <li>Plan: Premium</li>
            </ul>

            <p class="warn">Demo Only - No download allowed</p>
        </div>
    </body>
    </html>
    """

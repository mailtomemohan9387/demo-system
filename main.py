from fastapi import FastAPI, Form, Request
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

# Create files if not exists
if not os.path.exists(LEADS_FILE):
    with open(LEADS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Email", "Phone", "Company"])

if not os.path.exists(DEMO_FILE):
    with open(DEMO_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Email", "Token", "Expiry", "Used"])


def send_email(to, subject, html):
    try:
        requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": "onboarding@resend.dev",
                "to": [to],
                "subject": subject,
                "html": html,
            },
            timeout=15
        )
    except Exception as e:
        print("Mail error:", e)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <body style="font-family:Arial;background:#f5f7fb">
        <div style="max-width:600px;margin:40px auto;background:white;padding:30px;border-radius:12px">
            <h2>Demo Request</h2>
            <form action="/submit" method="post">
                <input name="name" placeholder="Name" required><br><br>
                <input name="email" placeholder="Email" required><br><br>
                <input name="phone" placeholder="Phone" required><br><br>
                <input name="company" placeholder="Company"><br><br>
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

    # RATE LIMIT CHECK
    with open(DEMO_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row[0] == email:
                expiry = datetime.fromisoformat(row[2])
                if now < expiry:
                    return "<h3>You already have active demo link. Check your email.</h3>"

    # SAVE LEAD
    with open(LEADS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name, email, phone, company])

    token = str(uuid.uuid4())
    expiry = now + timedelta(hours=1)

    # SAVE DEMO TOKEN
    with open(DEMO_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([email, token, expiry.isoformat(), "no"])

    # ONLY IMPORTANT CHANGE:
    demo_link = "https://nonacquisitive-kirk-bipyramidal.ngrok-free.dev/web/login"

    # EMAILS
    send_email(
        "mailtomemohan94@gmail.com",
        "New Demo Request",
        f"<b>{name}</b><br>{email}<br>{phone}<br>{company}"
    )

    send_email(
        email,
        "Thanks for contacting us",
        f"Hi {name},<br>We received your request."
    )

    send_email(
        email,
        "Your Demo Link",
        f"""
        Click below:<br>
        <a href="{demo_link}">Open Demo</a><br><br>
        Username: demo@demo.co<br>
        Password: demo
        """
    )

    return "<h3>Success! Check your email.</h3>"


@app.get("/demo/{token}", response_class=HTMLResponse)
def demo(token: str):
    rows = []
    valid_row = None

    with open(DEMO_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    for row in rows:
        if row[1] == token:
            valid_row = row
            break

    if not valid_row:
        return "<h3>Invalid link</h3>"

    email, token, expiry, used = valid_row
    expiry_time = datetime.fromisoformat(expiry)

    if datetime.now() > expiry_time:
        return "<h3>Link expired</h3>"

    if used == "yes":
        return "<h3>Link already used</h3>"

    # MARK USED
    for r in rows:
        if r[1] == token:
            r[3] = "yes"

    with open(DEMO_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Email", "Token", "Expiry", "Used"])
        writer.writerows(rows)

    return f"""
    <html>
    <body style="font-family:Arial;background:#f5f7fb">
        <div style="max-width:700px;margin:40px auto;background:white;padding:30px;border-radius:12px">
            <h2>Demo Access (Secure)</h2>
            <p>Welcome: {email}</p>

            <ul>
                <li>Customer: Demo User</li>
                <li>Invoice: ₹1000</li>
                <li>Status: Paid</li>
                <li>Plan: Premium</li>
            </ul>

            <p style="color:red">Read Only | No Download</p>
        </div>
    </body>
    </html>
    """

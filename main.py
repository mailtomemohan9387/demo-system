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

# Odoo login page link
ODOO_LOGIN_LINK = "https://nonacquisitive-kirk-bipyramidal.ngrok-free.dev/web/login"

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
    <head>
        <title>Book a Demo</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;font-family:Arial,Helvetica,sans-serif;background:linear-gradient(135deg,#eef4ff,#f8fbff);">
        <div style="max-width:820px;margin:40px auto;padding:20px;">
            <div style="background:#ffffff;border-radius:24px;padding:42px 36px;box-shadow:0 15px 40px rgba(0,0,0,0.08);border:1px solid #e8eefc;">
                
                <div style="text-align:center;margin-bottom:28px;">
                    <h1 style="margin:0;font-size:36px;color:#1f2a44;">Request a Live Demo</h1>
                    <p style="margin:14px 0 0;color:#5f6b85;font-size:16px;line-height:1.7;max-width:620px;margin-left:auto;margin-right:auto;">
                        Experience a professional, secure, and easy-to-use demo environment.
                        Submit your details and receive your demo access directly by email.
                    </p>
                </div>

                <div style="background:#f7faff;border:1px solid #e6eefc;border-radius:18px;padding:18px 20px;margin-bottom:26px;">
                    <div style="font-size:15px;color:#33415c;line-height:1.9;">
                        ✔ Fast demo access by email<br>
                        ✔ Safe customer-friendly experience<br>
                        ✔ Live product view with restricted access
                    </div>
                </div>

                <form action="/submit" method="post">
                    <div style="margin-bottom:18px;">
                        <label style="display:block;margin-bottom:8px;color:#25324a;font-weight:bold;">Full Name</label>
                        <input name="name" placeholder="Enter your full name" required
                            style="width:100%;padding:14px 16px;border:1px solid #d7e2f3;border-radius:12px;font-size:15px;box-sizing:border-box;outline:none;">
                    </div>

                    <div style="margin-bottom:18px;">
                        <label style="display:block;margin-bottom:8px;color:#25324a;font-weight:bold;">Email Address</label>
                        <input name="email" type="email" placeholder="Enter your email address" required
                            style="width:100%;padding:14px 16px;border:1px solid #d7e2f3;border-radius:12px;font-size:15px;box-sizing:border-box;outline:none;">
                    </div>

                    <div style="margin-bottom:18px;">
                        <label style="display:block;margin-bottom:8px;color:#25324a;font-weight:bold;">Phone Number</label>
                        <input name="phone" placeholder="Enter your phone number" required
                            style="width:100%;padding:14px 16px;border:1px solid #d7e2f3;border-radius:12px;font-size:15px;box-sizing:border-box;outline:none;">
                    </div>

                    <div style="margin-bottom:24px;">
                        <label style="display:block;margin-bottom:8px;color:#25324a;font-weight:bold;">Company Name</label>
                        <input name="company" placeholder="Enter your company name"
                            style="width:100%;padding:14px 16px;border:1px solid #d7e2f3;border-radius:12px;font-size:15px;box-sizing:border-box;outline:none;">
                    </div>

                    <button type="submit"
                        style="width:100%;background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#ffffff;border:none;border-radius:12px;padding:15px 18px;font-size:16px;font-weight:bold;cursor:pointer;box-shadow:0 10px 24px rgba(37,99,235,0.22);">
                        Submit Demo Request
                    </button>
                </form>

                <p style="margin:20px 0 0;text-align:center;color:#8a94a8;font-size:13px;">
                    By submitting this form, you will receive your demo access details by email.
                </p>
            </div>
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
                    return f"""
                    <html>
                    <head>
                        <title>Demo Already Sent</title>
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    </head>
                    <body style="margin:0;padding:0;font-family:Arial,Helvetica,sans-serif;background:linear-gradient(135deg,#eef4ff,#f8fbff);">
                        <div style="max-width:720px;margin:60px auto;padding:20px;">
                            <div style="background:#ffffff;border-radius:22px;padding:40px 34px;box-shadow:0 14px 35px rgba(0,0,0,0.08);border:1px solid #e8eefc;text-align:center;">
                                <h1 style="margin:0 0 14px;font-size:34px;color:#1f2a44;">Demo Link Already Active</h1>
                                <p style="margin:0;color:#5f6b85;font-size:16px;line-height:1.8;">
                                    Hi <b>{name}</b>, you already have an active demo link.<br>
                                    Please check your email inbox and use the latest demo email sent to you.
                                </p>

                                <div style="margin-top:26px;background:#f7faff;border:1px solid #e6eefc;border-radius:16px;padding:18px;">
                                    <p style="margin:0;color:#33415c;font-size:15px;">
                                        If you cannot find the email, please check your spam or promotions folder.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>
                    """

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

    # IMPORTANT:
    # Open Demo button should open Odoo login page directly
    demo_link = ODOO_LOGIN_LINK

    # ADMIN EMAIL
    send_email(
        "mailtomemohan94@gmail.com",
        "New Demo Request Received",
        f"""
        <div style="font-family:Arial,Helvetica,sans-serif;background:#f8fbff;padding:24px;">
            <div style="max-width:620px;margin:auto;background:#ffffff;border:1px solid #e6eefc;border-radius:18px;padding:28px;">
                <h2 style="margin-top:0;color:#1f2a44;">New Demo Request</h2>
                <p style="color:#5f6b85;line-height:1.8;margin:0;">
                    <b>Name:</b> {name}<br>
                    <b>Email:</b> {email}<br>
                    <b>Phone:</b> {phone}<br>
                    <b>Company:</b> {company if company else "-"}
                </p>
            </div>
        </div>
        """
    )

    # THANK YOU / WELCOME EMAIL
    send_email(
        email,
        "Thanks for Your Demo Request",
        f"""
        <div style="margin:0;padding:0;background:#f4f7fb;font-family:Arial,Helvetica,sans-serif;">
            <div style="max-width:640px;margin:30px auto;background:#ffffff;border-radius:18px;padding:36px 30px;border:1px solid #e6edf8;box-shadow:0 10px 30px rgba(0,0,0,0.08);">
                <h2 style="margin:0 0 14px;color:#1f2a44;">Welcome, {name}</h2>

                <p style="margin:0 0 14px;color:#5b6881;font-size:15px;line-height:1.8;">
                    Thank you for requesting a demo. Your request has been received successfully.
                </p>

                <p style="margin:0 0 14px;color:#5b6881;font-size:15px;line-height:1.8;">
                    We have prepared your demo access details and sent them in a separate email.
                    Please check your inbox for the next message titled <b>Your Demo Access Is Ready</b>.
                </p>

                <div style="background:#f8fbff;border:1px solid #e5edf9;border-radius:14px;padding:18px 20px;margin:20px 0;">
                    <p style="margin:0;color:#33415c;font-size:15px;line-height:1.8;">
                        ✔ Your request is confirmed<br>
                        ✔ Demo access details will arrive by email<br>
                        ✔ Please keep your login details secure
                    </p>
                </div>

                <p style="margin:18px 0 0;color:#8a94a8;font-size:13px;">
                    If you do not receive the email, please check your spam or promotions folder.
                </p>
            </div>
        </div>
        """
    )

    # DEMO ACCESS EMAIL
    send_email(
        email,
        "Your Demo Access Is Ready",
        f"""
        <div style="margin:0;padding:0;background:#f4f7fb;font-family:Arial,Helvetica,sans-serif;">
            <div style="max-width:640px;margin:30px auto;background:#ffffff;border-radius:18px;padding:36px 30px;border:1px solid #e6edf8;box-shadow:0 10px 30px rgba(0,0,0,0.08);">
                <h2 style="margin:0 0 14px;color:#1f2a44;">Your Demo Access Is Ready</h2>

                <p style="margin:0 0 14px;color:#5b6881;font-size:15px;line-height:1.8;">
                    Hello <b>{name}</b>,<br>
                    Your demo environment is ready. Click the button below to open the demo login page.
                </p>

                <div style="margin:24px 0;">
                    <a href="{demo_link}" style="display:inline-block;background:linear-gradient(135deg,#22c55e,#16a34a);color:#ffffff;text-decoration:none;padding:14px 26px;border-radius:12px;font-weight:bold;font-size:15px;">
                        Open Demo
                    </a>
                </div>

                <div style="background:#f8fbff;border:1px solid #e5edf9;border-radius:14px;padding:18px 20px;margin:20px 0;">
                    <p style="margin:0 0 10px;color:#1f2a44;font-weight:bold;">Demo Login Details</p>
                    <p style="margin:6px 0;color:#5b6881;">Username: <b>demo@demo.co</b></p>
                    <p style="margin:6px 0;color:#5b6881;">Password: <b>demo</b></p>
                </div>

                <div style="background:#fff8e7;border:1px solid #ffe1a8;border-radius:14px;padding:16px 18px;margin:20px 0;">
                    <p style="margin:0;color:#7a5b00;font-size:14px;line-height:1.8;">
                        <b>Important:</b><br>
                        • This demo is intended for product review only.<br>
                        • Some actions may be restricted in the demo environment.<br>
                        • If the login page appears, use the credentials above.
                    </p>
                </div>

                <p style="margin:18px 0 0;color:#8a94a8;font-size:13px;line-height:1.7;">
                    If the button does not work, copy and open this link manually:<br>
                    <span style="word-break:break-all;color:#2563eb;">{demo_link}</span>
                </p>
            </div>
        </div>
        """
    )

    return f"""
    <html>
    <head>
        <title>Request Submitted</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;font-family:Arial,Helvetica,sans-serif;background:linear-gradient(135deg,#eef4ff,#f8fbff);">
        <div style="max-width:760px;margin:60px auto;padding:20px;">
            <div style="background:#ffffff;border-radius:22px;padding:42px 34px;box-shadow:0 14px 35px rgba(0,0,0,0.08);border:1px solid #e8eefc;text-align:center;">
                <h1 style="margin:0 0 14px;font-size:34px;color:#1f2a44;">Thank You, {name}</h1>

                <p style="margin:0;color:#5f6b85;font-size:16px;line-height:1.8;">
                    Your demo request has been submitted successfully.
                </p>

                <div style="margin-top:24px;background:#f7faff;border:1px solid #e6eefc;border-radius:16px;padding:18px 20px;">
                    <p style="margin:0;color:#33415c;font-size:15px;line-height:1.8;">
                        ✔ We have received your request<br>
                        ✔ Your welcome email has been sent<br>
                        ✔ Your demo access email is on the way
                    </p>
                </div>

                <p style="margin:20px 0 0;color:#8a94a8;font-size:13px;">
                    Please check your inbox. If needed, also check your spam or promotions folder.
                </p>
            </div>
        </div>
    </body>
    </html>
    """


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
        return """
        <html>
        <body style="font-family:Arial,Helvetica,sans-serif;background:#f8fbff;">
            <div style="max-width:700px;margin:60px auto;background:#fff;padding:30px;border-radius:18px;border:1px solid #e8eefc;box-shadow:0 10px 25px rgba(0,0,0,0.08);text-align:center;">
                <h2 style="color:#1f2a44;">Invalid Link</h2>
                <p style="color:#5f6b85;">The demo link is not valid.</p>
            </div>
        </body>
        </html>
        """

    email, token, expiry, used = valid_row
    expiry_time = datetime.fromisoformat(expiry)

    if datetime.now() > expiry_time:
        return """
        <html>
        <body style="font-family:Arial,Helvetica,sans-serif;background:#f8fbff;">
            <div style="max-width:700px;margin:60px auto;background:#fff;padding:30px;border-radius:18px;border:1px solid #e8eefc;box-shadow:0 10px 25px rgba(0,0,0,0.08);text-align:center;">
                <h2 style="color:#1f2a44;">Link Expired</h2>
                <p style="color:#5f6b85;">This demo link has expired.</p>
            </div>
        </body>
        </html>
        """

    if used == "yes":
        return """
        <html>
        <body style="font-family:Arial,Helvetica,sans-serif;background:#f8fbff;">
            <div style="max-width:700px;margin:60px auto;background:#fff;padding:30px;border-radius:18px;border:1px solid #e8eefc;box-shadow:0 10px 25px rgba(0,0,0,0.08);text-align:center;">
                <h2 style="color:#1f2a44;">Link Already Used</h2>
                <p style="color:#5f6b85;">This demo link has already been used.</p>
            </div>
        </body>
        </html>
        """

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
    <head>
        <title>Demo Access</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;font-family:Arial,Helvetica,sans-serif;background:linear-gradient(135deg,#eef4ff,#f8fbff);">
        <div style="max-width:760px;margin:50px auto;padding:20px;">
            <div style="background:#ffffff;border-radius:22px;padding:38px 34px;box-shadow:0 14px 35px rgba(0,0,0,0.08);border:1px solid #e8eefc;">
                <div style="text-align:center;margin-bottom:26px;">
                    <h1 style="margin:0;font-size:34px;color:#1f2a44;">Demo Access</h1>
                    <p style="margin:12px 0 0;color:#5f6b85;font-size:16px;line-height:1.6;">
                        Your access has been verified successfully.
                    </p>
                </div>

                <div style="background:#f8fbff;border:1px solid #e5edf9;border-radius:16px;padding:18px 20px;margin-bottom:24px;">
                    <p style="margin:0;color:#33415c;font-size:15px;line-height:1.8;">
                        <b>Welcome:</b> {email}<br>
                        <b>Access Type:</b> Read Only Demo<br>
                        <b>Validity:</b> 1 Hour
                    </p>
                </div>

                <div style="background:#ffffff;border:1px solid #edf2fb;border-radius:16px;padding:20px 22px;box-shadow:inset 0 0 0 1px #f7faff;">
                    <h3 style="margin:0 0 16px;color:#22314d;">Demo Details</h3>
                    <ul style="margin:0;padding-left:20px;color:#51607a;line-height:2;font-size:15px;">
                        <li>Customer: Demo User</li>
                        <li>Invoice: ₹1000</li>
                        <li>Status: Paid</li>
                        <li>Plan: Premium</li>
                    </ul>
                </div>

                <div style="margin-top:26px;padding:16px 18px;background:#fff5f5;border:1px solid #ffd9d9;border-radius:14px;color:#c62828;font-weight:bold;">
                    Demo Only - No download allowed
                </div>
            </div>
        </div>
    </body>
    </html>
    """

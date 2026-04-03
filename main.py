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
        <div style="font-family:Arial,sans-serif;line-height:1.6">
            <h2>New Demo Request</h2>
            <p><b>Name:</b> {name}</p>
            <p><b>Email:</b> {email}</p>
            <p><b>Phone:</b> {phone}</p>
            <p><b>Company:</b> {company}</p>
        </div>
        """
    }

    user_data = {
        "from": "onboarding@resend.dev",
        "to": [email],
        "subject": "Thanks for contacting us",
        "html": f"""
        <div style="font-family:Arial,sans-serif;line-height:1.6">
            <h2>Thanks for contacting us</h2>
            <p>Hi {name},</p>
            <p>Thanks for your interest.</p>
            <p>We have received your demo request successfully.</p>
            <p>Our team will contact you shortly.</p>
            <p>Regards,<br>Mohan</p>
        </div>
        """
    }

    try:
        admin_response = requests.post(url, json=admin_data, headers=headers, timeout=15)
        user_response = requests.post(url, json=user_data, headers=headers, timeout=15)

        print("Admin mail status:", admin_response.status_code)
        print("User mail status:", user_response.status_code)
        print("Admin mail response:", admin_response.text)
        print("User mail response:", user_response.text)

    except Exception as e:
        print("Email error:", e)


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
    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([name, email, phone, company])

    send_email(name, email, phone, company)

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

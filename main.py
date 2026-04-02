from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import os
import csv
import requests

app = FastAPI()

# Resend API Key
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# CSV file
csv_file = "leads.csv"

# Create CSV file with header if not exists
if not os.path.exists(csv_file):
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Email", "Phone", "Company"])


def send_email(name, email, phone, company):
    url = "https://api.resend.com/emails"

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    # 1. Admin mail
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

    # 2. Customer auto reply
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

    admin_response = requests.post(url, json=admin_data, headers=headers)
    print("Admin mail:", admin_response.text)

    user_response = requests.post(url, json=user_data, headers=headers)
    print("User mail:", user_response.text)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Demo System</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 40px auto;
                    padding: 20px;
                    line-height: 1.6;
                }
                h1 {
                    margin-bottom: 10px;
                }
                form {
                    margin-top: 20px;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                }
                input {
                    width: 100%;
                    padding: 10px;
                    margin-top: 5px;
                    margin-bottom: 15px;
                    border: 1px solid #ccc;
                    border-radius: 6px;
                    box-sizing: border-box;
                }
                button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 18px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #45a049;
                }
            </style>
        </head>
        <body>
            <h1>Demo Request Form</h1>
            <p>Please enter your details below.</p>

            <form action="/submit" method="post">
                <label>Name:</label>
                <input type="text" name="name" required>

                <label>Email:</label>
                <input type="email" name="email" required>

                <label>Phone:</label>
                <input type="text" name="phone" required>

                <label>Company:</label>
                <input type="text" name="company">

                <button type="submit">Submit</button>
            </form>
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
    # Save to CSV
    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([name, email, phone, company])

    try:
        if not RESEND_API_KEY:
            raise Exception("RESEND_API_KEY not set")

        send_email(name, email, phone, company)

    except Exception as e:
        print("Error:", e)

    return f"""
    <html>
        <head>
            <title>Success</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
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
                    color: white;
                    background: #4CAF50;
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

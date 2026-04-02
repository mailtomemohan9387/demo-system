from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import smtplib
import os
import csv
from email.mime.text import MIMEText

app = FastAPI()

# Secure config from environment variables
sender_email = os.getenv("GMAIL_USER")
sender_password = os.getenv("GMAIL_APP_PASSWORD")

# CSV file name
csv_file = "leads.csv"

# Create CSV file with header if not exists
if not os.path.exists(csv_file):
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Email", "Phone", "Company"])


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
                .note {
                    color: #555;
                }
            </style>
        </head>
        <body>
            <h1>Demo Request Form</h1>
            <p class="note">Please enter your details below.</p>

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
        if not sender_email or not sender_password:
            raise Exception("Email environment variables not set")

        # 1. Send lead email to admin
        subject_admin = "New Lead Received"
        body_admin = f"""
New Customer Details:

Name: {name}
Email: {email}
Phone: {phone}
Company: {company}
"""

        msg_admin = MIMEText(body_admin)
        msg_admin["Subject"] = subject_admin
        msg_admin["From"] = sender_email
        msg_admin["To"] = sender_email

        # 2. Send auto reply to customer
        subject_user = "Thanks for contacting us"
        body_user = f"""
Hi {name},

Thanks for your interest.

We have received your demo request.
Our team will contact you shortly.

Regards,
Mohan
"""

        msg_user = MIMEText(body_user)
        msg_user["Subject"] = subject_user
        msg_user["From"] = sender_email
        msg_user["To"] = email

        # SMTP send
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        server.send_message(msg_admin)
        server.send_message(msg_user)

        server.quit()

        print("Both Emails Sent Successfully")

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

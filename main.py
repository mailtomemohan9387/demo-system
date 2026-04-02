from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import smtplib
import os
import csv
from email.mime.text import MIMEText

app = FastAPI()

# Secure config
sender_email = os.getenv("GMAIL_USER")
sender_password = os.getenv("GMAIL_APP_PASSWORD")

# CSV file
csv_file = "leads.csv"

# Create CSV file if not exists
if not os.path.exists(csv_file):
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Email", "Phone", "Company"])


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Lead Form</title>
        </head>
        <body>
            <h1>Welcome Mohan</h1>
            <p>Your Automation System is Working!</p>

            <h2>Enter Details</h2>

            <form action="/submit" method="post">
                <label>Name:</label><br>
                <input type="text" name="name" required><br><br>

                <label>Email:</label><br>
                <input type="email" name="email" required><br><br>

                <label>Phone:</label><br>
                <input type="text" name="phone" required><br><br>

                <label>Company:</label><br>
                <input type="text" name="company"><br><br>

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
    with open(csv_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name, email, phone, company])

    try:
        if not sender_email or not sender_password:
            raise Exception("Email environment variables not set")

        # 🔥 1. Send lead mail to YOU
        subject_admin = "🔥 New Lead Received"
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

        # 🔥 2. Send auto reply to CUSTOMER
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

        server.send_message(msg_admin)  # to you
        server.send_message(msg_user)   # to customer

        server.quit()

        print("Both Emails Sent Successfully")

    except Exception as e:
        print("Error:", e)

    return f"""
    <html>
        <head>
            <title>Success</title>
        </head>
        <body>
            <h2>Saved Successfully</h2>
            <p><b>Name:</b> {name}</p>
            <p><b>Email:</b> {email}</p>
            <p><b>Phone:</b> {phone}</p>
            <p><b>Company:</b> {company}</p>
            <p>We will contact you soon.</p>
        </body>
    </html>
    """

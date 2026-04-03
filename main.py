from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import csv, os, requests, uuid
from datetime import datetime, timedelta

app = FastAPI()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

LEADS_FILE = "leads.csv"
DEMO_FILE = "demo_links.csv"

# create files if not exist
if not os.path.exists(LEADS_FILE):
    with open(LEADS_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["Name", "Email", "Phone", "Company"])

if not os.path.exists(DEMO_FILE):
    with open(DEMO_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["Email", "Token", "Expiry"])


# 🔹 email send
def send_email(email, demo_link):
    if not RESEND_API_KEY:
        return

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "from": "onboarding@resend.dev",
        "to": [email],
        "subject": "Your Demo Access Link",
        "html": f"""
        <h2>Demo Access</h2>
        <p>Your demo link is valid for 1 hour.</p>
        <a href="{demo_link}">Click here to access demo</a>
        """
    }

    try:
        requests.post(url, json=data, headers=headers, timeout=10)
    except:
        pass


# 🔹 home form
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>Demo Request</h2>
    <form action="/submit" method="post">
        Name: <input name="name"><br><br>
        Email: <input name="email"><br><br>
        Phone: <input name="phone"><br><br>
        Company: <input name="company"><br><br>
        <button type="submit">Submit</button>
    </form>
    """


# 🔹 submit
@app.post("/submit", response_class=HTMLResponse)
def submit(name: str = Form(...), email: str = Form(...), phone: str = Form(...), company: str = Form("")):

    # save lead
    with open(LEADS_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([name, email, phone, company])

    # generate token
    token = str(uuid.uuid4())

    # expiry = 1 hour
    expiry = datetime.now() + timedelta(hours=1)

    # save token
    with open(DEMO_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([email, token, expiry])

    # demo link
    demo_link = f"https://demo-system-9qv6.onrender.com/demo/{token}"

    # send email
    send_email(email, demo_link)

    return f"<h2>Demo link sent to {email}</h2>"


# 🔹 demo access
@app.get("/demo/{token}", response_class=HTMLResponse)
def demo(token: str):

    valid = False

    with open(DEMO_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            saved_token = row[1]
            expiry = datetime.fromisoformat(row[2])

            if saved_token == token:
                if datetime.now() < expiry:
                    valid = True
                break

    if not valid:
        return "<h2>Link expired or invalid</h2>"

    return """
    <h2>Demo Access (Read Only)</h2>
    <p>This is demo environment</p>

    <ul>
        <li>Customer: Demo User</li>
        <li>Invoice: ₹1000</li>
        <li>Status: Paid</li>
    </ul>

    <p style="color:red;">Demo Only - No download allowed</p>
    """

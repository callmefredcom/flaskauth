import requests
import json
from dotenv import load_dotenv
load_dotenv()
import os

# Set up the API key and endpoint
api_key = os.environ.get('SENDINBLUE')
url = "https://api.sendinblue.com/v3/smtp/email"

def send_welcome_email(email):

    params1 = {
        "sender": {"name": "Frederick | The Best App", "email": "youremail@yoursite.com"},
        "to": [{"email": f"{email}"}],
        "subject": "Welcome on The Best App",
        "htmlContent": "Hi there!<br><br>Thanks so much for joining The Best App, the easiest way to create stuff on the web<br><br>"
        "You can start creating your stuff on <a href='https://www.yourcompany.com/app'>www.yourcompany.com/app</a>."
        "<br><br>Don't hesitate to reach out if you have any questions or feedback."            
         "<br><br>Speak soon,<br><br>Frederick,<br>The Best App",
    }

    params2 = {
        "sender": {"name": "The Best App", "email": "contact@callmefred.com"},
        "to": [{"email": "youremail@gmail.com"}],
        "subject": "🤘 NEW USER SIGNUP",
        "htmlContent": f"A new user has just signed up.<br><br>📧 User's Email: {email}",
    }

    headers = {"api-key": api_key, "Content-Type": "application/json"}

    response1 = requests.post(url, headers=headers, data=json.dumps(params1))

    response2 = requests.post(url, headers=headers, data=json.dumps(params2))

    if response1.status_code == 201:

        print("Email 1 sent successfully!")

    else:
        print("An error occurred: ", response1.text)

    if response2.status_code == 201:

        print("Email 2 sent successfully!")

    else:
        print("An error occurred: ", response2.text)


    return "Emails sent successfully!"


def send_mail_pw_reset(recipient, reset_url):

    headers = {"api-key": api_key, "Content-Type": "application/json"}

    params = {
        "sender": {"name": "The Best App", "email": "youremail@yoursite.com"},
        "to": [{"email": f"{recipient}"}],
        "subject": "Password Reset Request",
        "htmlContent": f"Hi there!<br><br>You have requested to reset your password.<br><br>Please click on the following link to choose a new password: {reset_url}<br><br>If it wasn't you, please ignore this message.<br><br>Best,<br><br>Frederick,<br>The Best App",
    }

    response = requests.post(url, headers=headers, data=json.dumps(params))

    if response.status_code == 201:

        print("Email 1 sent successfully!")

    else:
        print("An error occurred: ", response.text)


def send_mail_verification(recipient, verification_url):
    headers = {"api-key": api_key, "Content-Type": "application/json"}

    params = {
        "sender": {"name": "The Best App", "email": "youremail@yoursite.com"},
        "to": [{"email": f"{recipient}"}],
        "subject": "Email Verification Request",
        "htmlContent": f"Hi there!<br><br>Please verify your email address for The Best App.<br><br>Click on the following link to verify: {verification_url}<br><br>If it wasn't you, please ignore this message.<br><br>Best,<br><br>Frederick,<br>The Best App",
    }

    response = requests.post(url, headers=headers, data=json.dumps(params))

    if response.status_code == 201:
        print("Verification email sent successfully!")
    else:
        print("An error occurred: ", response.text)


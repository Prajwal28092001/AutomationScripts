"""
Quick script to verify email_config.json works.
Run:  python test_email.py
"""
import json, os, smtplib
from email.message import EmailMessage

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "email_config.json")

with open(config_path) as f:
    config = json.load(f)

sender    = config["sender_email"]
pwd       = config["sender_password"]
recipient = config["recipient_email"]

msg = EmailMessage()
msg["Subject"] = "Test Email - Automation Setup Check"
msg["From"]    = sender
msg["To"]      = recipient
msg.set_content("If you received this, your email setup is working correctly!")
msg.add_alternative(
    "<html><body><h2 style='color:green;'>✅ Email is working!</h2>"
    "<p>Your <code>email_config.json</code> is configured correctly.</p>"
    "</body></html>",
    subtype="html",
)

print(f"Connecting to smtp.gmail.com:465 ...")
print(f"  From:  {sender}")
print(f"  To:    {recipient}")

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, pwd)
        server.send_message(msg)
    print("\n✅ SUCCESS — Email sent! Check the recipient inbox.")
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ AUTHENTICATION FAILED: {e}")
    print("\nYou are likely using your regular Gmail password.")
    print("Gmail requires an App Password for SMTP.")
    print("Steps to fix:")
    print("  1. Go to https://myaccount.google.com/security")
    print("  2. Enable 2-Step Verification (if not already)")
    print("  3. Go to https://myaccount.google.com/apppasswords")
    print("  4. Generate a new App Password for 'Mail'")
    print("  5. Replace sender_password in email_config.json with the 16-char app password")
except Exception as e:
    print(f"\n❌ FAILED: {e}")

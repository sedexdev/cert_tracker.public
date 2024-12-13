#!/usr/bin/python3

"""
Script for testing sending email using 
smtplib and GMail
"""

# pylint: disable=broad-exception-caught, line-too-long

import datetime
import json
import os
import smtplib

from email.mime.text import MIMEText

CERT_CODE = os.environ["CERT_CODE"]

# read base and cert data from data.json
with open("./data.json", "r", encoding="utf-8") as file:
    data = json.loads(file.read())

# setup email params
SENDER = data["sender"]
PASSWORD = data["token"]
RECIPIENT = data["recipient"]
SUBJECT = "Cert Tracker exam reminder"

# get the cert details from the data
cert_name = data[CERT_CODE]["name"]
cert_code = data[CERT_CODE]["code"]
exam_date = data[CERT_CODE]["examDate"]

# calculate days till exam
today = datetime.date.today()
exam_split = exam_date.split("-")
year = int(exam_split[0])
month = int(exam_split[1])
day = int(exam_split[2])
days = datetime.date(year, month, day) - today

# update exam date for UK format
EXAM_DATE = f"{day}-{month}-{year}"

BODY = f"""
<html>
    <body style="padding: 0; margin: 0;">
        <table align="center" width="90%" style="font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif; max-width: 600px; margin: auto; text-align: center;">
            <tr>
                <td>
                    <p style="font-size: 48px; font-weight: bold; color: rgb(233, 198, 0); padding: 0;">Cert Tracker</p>
                </td>
            </tr>
            <tr>
                <td style="font-size: 24px; padding: 0 0 30px 0;">
                    Your {cert_name} - {cert_code} exam is booked for
                    <span style="color: darkcyan;">{EXAM_DATE}</span>
                </td>
            </tr>
            <tr>
                <td bgcolor="#32CD32" style="color: white; font-size: 20px; padding: 20px;">
                    <table width="100%">
                        <tr>
                            <td align="center" style="padding: 25px;">You have</td>
                        </tr>
                        <tr>
                            <td align="center" style="font-size: 40px; font-weight: bold; padding: 10px;">{days.days}</td>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 25px;">days to go!</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
</html>
"""

# create html message content
html = MIMEText(BODY, "html")
html["Subject"] = SUBJECT
html["From"] = SENDER
html["To"] = RECIPIENT

# connect to Google SMTP and send email
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.ehlo()
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, RECIPIENT, html.as_string())
        print("Message sent successfully :)")
except Exception as e:
    print(f"Failed to send email: {e}")

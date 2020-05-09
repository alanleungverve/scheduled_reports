### Looker API resources: https://github.com/looker-open-source/sdk-codegen ###

#Import dump
import json
import urllib
import sys
import textwrap
import time
import os
import email, smtplib, ssl
import looker_sdk

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import cast, Dict, Optional
from looker_sdk import models

#Create a folder where you can store the pdfs.
os.mkdir("~/Desktop/campaign_performance")

#API credentials here to access Looker
sdk = looker_sdk.init31("~/Projects/looker_projects/looker.ini")

"""
Generate a dataframe of user_ids, names, emails, and list of campaign ids
"""

directory = "~/Desktop/campaign_performance/"

#Placeholder list - perhaps a dict with k,v of user_id to campaign_id?
user_id = [
    "alan"
    , "lukasz"
    , "betul"
]

#Function to generate a list of campaign reports per user
#This may be an issue once a user has a large list of campaigns - may want to upload to a Google drive instead of email.
def file_gen():
    for user in user_id:
        #Creates a directory with the user_id so that we can identify who gets which reports.
        os.mkdir(directory + user)

        #Placeholder list for a dynamically generated list of campaigns per user.
        campaign_id = [
            "4e14ee50-76ab-4e51-a8b7-8ffcdc955397",
            "fdc98a75-f27b-4f3f-ac50-1383900a5747",
            "e65948dd-1355-46e4-930b-5f31bcc552c6"
        ]
        for cid in campaign_id:
            def get_pdf():
                filters = '?Campaign%20Name=&Campaign%20ID=' + cid + '&filter_config=%7B"Campaign%20Name":%5B%7B"type":"%3D","values":%5B%7B"constant":""%7D,%7B%7D%5D,"id":22%7D%5D,"Campaign%20ID":%5B%7B"type":"%3D","values":%5B%7B"constant":"' + cid + '"%7D,%7B%7D%5D,"id":23%7D%5D%7D'
                dashboard_number=326
                task = sdk.create_dashboard_render_task(
                    dashboard_id=dashboard_number,
                    result_format="pdf",
                    body=models.CreateDashboardRenderTask(
                        dashboard_style="tiled",
                        dashboard_filters=filters
                    ),
                    width=545,
                    height=842
                )

                if not (task and task.id):
                    print("Render failed")

                # poll the render task until it completes
                elapsed = 0.0
                delay = 0.5  # wait .5 seconds
                while True:
                    poll = sdk.render_task(task.id)
                    if poll.status == "failure":
                        print(poll)
                        print("Render failed")
                    elif poll.status == "success":
                        break

                    time.sleep(delay)
                    elapsed += delay
                print(f"Render task completed in {elapsed} seconds")

                result = sdk.render_task_results(task.id)
                filename = directory + user + "/" + cid + "_file.pdf"
                with open(filename, "wb") as f:
                    f.write(result)
                print(f'Dashboard pdf saved as "{filename}"')

            get_pdf()
file_gen()

#Function to group attachments into one email per user.

filename = []
for user in user_id:
    for root, dirs, files in os.walk(directory + user):
        for file in files:
            if file.endswith('.pdf'):
                filename.append(file)

for user in user_id:
    def email_gen():

        #Change these values accordingly
        subject = "Pollen Campaign Performance Report"
        body = "Hi there, here is your campaign performance report."
        sender_email = "SENDER_EMAIL@pollen.co"
        receiver_email = "RECEIVER_EMAIL@pollen.co"
        password = "PASSWORD" #alternatively use this -> input("Type your password and press enter:")

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = "SENDER_EMAIL@pollen.co"
        message["To"] = "RECEIVER_EMAIL@pollen.co"
        message["Subject"] = "Report for " + user

        # Add body to email
        message.attach(MIMEText(body, "plain"))
        
        for f in filename:
            g = directory + user + "/" + f
            # Open PDF file in binary mode
            with open(g, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email    
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {g}",
            )

            # Add attachment to message and convert message to string
            message.attach(part)
            text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)

    email_gen()

print("Done!")

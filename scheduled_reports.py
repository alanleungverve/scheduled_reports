### Looker API resources: https://github.com/looker-open-source/sdk-codegen ###
#Notes: To send out emails from your Google account using this script, you will need to enable Insecure Apps.
#Otherwise the script will fail.

#Import dump
import time
import os
import shutil
import email, smtplib, ssl
import looker_sdk
import pandas as pd

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import cast, Dict, Optional
from looker_sdk import models

#API credentials here to access Looker
try:
    sdk = looker_sdk.init31("/Users/alanleung/Projects/looker_projects/looker.ini")
except:
    print("Authentication failed.")

#Create a folder where you can store the pdfs.
os.mkdir("/Users/alanleung/Desktop/campaign_performance")
directory = "/Users/alanleung/Desktop/campaign_performance/"

#Generate dataframes. 
#test.csv is a csv file that provides the user_id, user_email, and campaign_id.
#Currently, it assumes a fan out on campaign_id - there is list aggregation/deaggregation in the script.
#test.csv format is user_id (int) | user_email (str) | campaign_id (str)
df = pd.read_csv("/Users/alanleung/Desktop/test.csv")
df2 = df.groupby('user_id')['campaign_id'].apply(list).reset_index(name='campaign_id')

user_id = []
for rows in df.itertuples():
    my_list = rows.user_id
    if (str(my_list)) not in user_id:
        user_id.append(str(my_list))

#Function to generate a list of campaign reports per user
#This may be an issue once a user has a large list of campaigns - may want to upload to a Google drive instead of email.
def file_gen():
    for user in user_id:
        #Creates a directory with the user_id so that we can identify who gets which reports.
        os.mkdir(directory + user)
        
        campaign_id = df2.loc[df2['user_id'] == int(user)]

        for cid_list in campaign_id['campaign_id']:
            for cid in cid_list:
                def get_pdf():
                    filters = '?Campaign%20Name=&Campaign%20ID=' + str(cid) + '&filter_config=%7B"Campaign%20Name":%5B%7B"type":"%3D","values":%5B%7B"constant":""%7D,%7B%7D%5D,"id":22%7D%5D,"Campaign%20ID":%5B%7B"type":"%3D","values":%5B%7B"constant":"' + str(cid) + '"%7D,%7B%7D%5D,"id":23%7D%5D%7D'
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
                    filename = directory + user + "/" + str(cid) + "_file.pdf"
                    with open(filename, "wb") as f:
                        f.write(result)
                    print(f'Dashboard pdf saved as "{filename}"')

                get_pdf()
file_gen()

print("PDFs have been generated.")

#Function to group attachments into one email per user.

filename = []
for user in user_id:
    for root, dirs, files in os.walk(directory + user):
        for file in files:
            if file.endswith('.pdf'):
                if file not in filename:
                    filename.append(directory + user + "/" + str(file))

for user in user_id:
    def email_gen():

        #Change these values accordingly - currently set for testing. You can pass through values from test.csv
        #using the user_email column.
        subject = "Pollen Campaign Performance Report"
        body = "Hi there, here is your campaign performance report."
        sender_email = "alan.leung@pollen.co"
        receiver_email = "alan.leung@pollen.co"
        password = "SOME_COMPLICATED_AND_UNBREAKABLE_PASSWORD" #alternatively use this -> input("Type your password and press enter:")

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = "alan.leung@pollen.co"
        message["To"] = "alan.leung@pollen.co"
        message["Subject"] = "Report for " + user

        # Add body to email
        message.attach(MIMEText(body, "plain"))
        
        for f in filename:
            # Open PDF file in binary mode
            with open(f, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email    
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {f}",
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
print("Emails sent.")

#Removes the directory for cleanliness (which I've heard is next to godliness, but I could be mistaken.)
shutil.rmtree(directory)
print("Directory has been removed.")

print("Done!")

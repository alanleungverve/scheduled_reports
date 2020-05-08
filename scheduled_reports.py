### Looker API resources: https://github.com/looker-open-source/sdk-codegen ###

import json
import urllib
import sys
import textwrap
import time
import os
import email, smtplib, ssl
import looker_sdk
#import pandas as pd

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import cast, Dict, Optional
from looker_sdk import models

#API credentials here to access Looker
sdk = looker_sdk.init31("/Users/alanleung/Projects/looker_projects/looker.ini")

"""
Generate a dataframe of user_ids, names, emails, and list of campaign ids
"""

#Placeholder list - perhaps a dict with k,v of user_id to campaign_id?
user_id = [
    "alan"
    , "lukasz"
    , "betul"
]

#Function to generate a list of campaign reports per user
#This may be an issue once a user has a large list of campaigns - may want to upload to a Google drive instead of email.
def file_gen():
    for k in user_id:
        #Creates a directory with the user_id so that we can identify who gets which reports.
        os.mkdir("/Users/alanleung/Desktop/campaign_performance/" + k)

        #Placeholder list for a dynamically generated list of campaigns per user.
        campaign_id = [
            "4e14ee50-76ab-4e51-a8b7-8ffcdc955397",
            "fdc98a75-f27b-4f3f-ac50-1383900a5747",
            "e65948dd-1355-46e4-930b-5f31bcc552c6"
        ]
        for i in campaign_id:
            def get_pdf():
                filters = '?Campaign%20Name=&Campaign%20ID=' + i + '&filter_config=%7B"Campaign%20Name":%5B%7B"type":"%3D","values":%5B%7B"constant":""%7D,%7B%7D%5D,"id":22%7D%5D,"Campaign%20ID":%5B%7B"type":"%3D","values":%5B%7B"constant":"' + i + '"%7D,%7B%7D%5D,"id":23%7D%5D%7D'
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
                filename = "/Users/alanleung/Desktop/campaign_performance/" + k + "/" + i + "_file.pdf"
                with open(filename, "wb") as f:
                    f.write(result)
                print(f'Dashboard pdf saved as "{filename}"')

            get_pdf()
file_gen()

#Function to group attachments into one email per user.
"""
def gen_email():
    for folder in campaign_performance folder:
        for file in individual_user folders:
            generate an email
            add all files as attachments
            send
            delete files
gen_email()
"""

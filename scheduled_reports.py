# Scheduled Reports script

from time import time
from looker_sdk import client, models, error

start_time = time()

# client calls will now automatically authenticate using the
# api3credentials specified in 'looker.ini'
sdk = client.setup("looker.ini")
looker_api_user = sdk.me()

# create an instance of the API class
# Set up the list of users
users_list = [14]  # int | Id of user

# Set up the "Campaign Performace" dashboard for schedule 
scheduled_dashboard = 326

print("------------------------------------------")

# Set up the Nass Festival 2020 as a test campaign
campaign_name = "NASS Festival 2020"

# Set up the cron tab every day at 07:00 BST
cron_tab = "0 7 * * *"

# Set up the test schedule email address 
# email = 'lukasz.aszyk@pollen.co'
email = "alan.leung@pollen.co"
start_time = time()
for user_id in users_list:
    try:
        # Setting up the schedule name and the body of the scheduler
        schedule_name = "Campaign Performance for " + campaign_name
        body = {
            "name": schedule_name,
            "user_id": user_id,
            "run_as_recipient": False,
            "enabled": True,
            "dashboard_id": scheduled_dashboard,
            "filters_string": "?Campaign%20Name=NASS%20Festival%202020&filter_config=%7B%22Campaign%20Name%22:%5B%7B%22type%22:%22%3D%22,%22values%22:%5B%7B%22constant%22:={}".format(
                campaign_name
            ),
            "require_results": False,
            "require_no_results": False,
            "require_change": False,
            "send_all_results": False,
            "crontab": cron_tab,
            "timezone": "Europe/London",
            "scheduled_plan_destination": [
                {
                    "format": "wysiwyg_pdf",
                    "apply_formatting": True,
                    "apply_vis": True,
                    "address": email,
                    "type": "email",
                }
            ],
            "include_links": False,
        }

        # Creating the schedule one user at a time
        sdk.create_scheduled_plan(body)
        value = sdk.scheduled_plans_for_dashboard(
            dashboard_id=scheduled_dashboard
        )
        # Print values for validation
        print(value[0])
        print(
            "Dashboard name:",
            value[0].name,
            ", User ID:",
            value[0].user_id,
            ", Schedule address:",
            value[0].scheduled_plan_destination[0].address,
            ", Filter value",
            value[0].filters_string,
        )
    except:
        print("Exception when calling UserApi->set_user_attribute_user_value: %s\n" % e)

end_time = time()

print("------------------------------------------")
print("The process took", round(end_time - start_time, 2), "seconds to run")

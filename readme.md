__Solution Overview__

Currently, Looker produces one email per PDF when generating a report on campaign performance.
This is not acceptable when external stakeholders are members of multiple campaigns. The
scheduled reports script will try to remedy this by downloading all PDFs on a per-stakeholder
basis, storing it locally, aggregating them into one email, sending out the email, and then 
removing the directory when the script finishes running.

__Solution Limitations__

There are certain limitations to this solution. First, it will take some time to run due to the
serial nature of the API calls - we can only generate 1 PDF at a time. Given that it takes 15 
seconds to render the data and generate a PDF on average, it will take about 2 hours to generate
a PDF report per stakeholder for 350 stakeholders. We may want to investigate decoupling this script
from a local machine and instead host it on a cloud instance. Second, if a stakeholder is a member 
of many campaigns, the email may exceed Gmail's email size limits. One potential solution is 
that we upload the PDFs to a Google Drive folder and email out a shared link instead.

# hyperflex-notification-tool
The HyperFlex Notification Tool (HXNT) provides email alert notifications on the status of Cisco HyperFlex Edge cluster deployments through Cisco Intersight.
No longer do you have to manually check or monitor the Intersight web GUI to find out the status of your deployment.
HXNT will automatically provide updates on HyperFlex deployment completions, failures, required pending changes, and missing cluster profiles.

## Requirements:
  1. Python 3.
  2. The Cisco Intersight SDK installed, available by running: "pip install git+https://github.com/CiscoUcs/intersight-python.git". More information can be found at https://github.com/CiscoUcs/intersight-python.
  3. An API key from your Intersight account.
  4. A reachable SMTP server.
  
### Author:
Ugo Emekauwa

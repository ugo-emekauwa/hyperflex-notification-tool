"""
HyperFlex Notification Tool (HXNT), v1.0
Author: Ugo Emekauwa
Contact: uemekauw@cisco.com, uemekauwa@gmail.com
Summary: The HyperFlex Notification Tool will provide email notification alerts for
          the deployment of Cisco HyperFlex Edge clusters through Cisco Intersight.
"""

# Import needed Python modules
import sys
import os
import logging
import time
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE, formatdate
from email.mime.base import MIMEBase
from email import encoders
from os.path import basename
import intersight
from intersight.intersight_api_client import IntersightApiClient

# Define time variable
get_date = datetime.datetime.now()
date = get_date.strftime("%m/%d/%Y %H:%M:%S")

# HyperFlex Edge Notification Tool Banner and Greeting

print("                                   <HX Notification Tool>\n\n")
print("Hello!\n")
print("The HX Notification Tool (HXNT) will send email notifications \non the status of your HyperFlex Edge cluster deployment.")

# Begin User Questions
# Request user to input the Intersight API key ID
while True:
  while True:
    key_id_answer = input("\nPlease enter the API key ID for your Intersight account:\n")
    key_id = key_id_answer.strip()
    if len(key_id) is not 0 and "/" in key_id: break
    print("That answer is invalid.")
  # Request user to input the Intersight API secret key path
  while True:
    key_answer = input("\nPlease enter the path to the matching API secret key file:\n")
    key = key_answer.strip()
    if len(key) is not 0 and os.path.isfile(key): break
    print("The path or specified secret key file does not exist or is invalid.")
    print("Please verify the path and/or file and enter it again")

  print("\nTesting access to the Intersight API...\n")
  try:
    # Define Intersight SDK IntersightApiClient variables
    # Tested on Cisco Intersight API Reference v1.0.9-740
    base_url = "https://intersight.com/api/v1"
    api_instance = IntersightApiClient(host=base_url,private_key=key,api_key_id=key_id)
    check_account = intersight.apis.iam_account_api.IamAccountApi(api_instance)
    get_account = check_account.iam_accounts_get()
    if check_account.api_client.last_response.status is not 200:
      print("The Intersight API Test was unable to verify the account information.")
      print("Please verify that the API key information entered was correct.")
      print("Also check https://status.intersight.com to verify \nthe Intersight service is available.\n")
      print("If the above troubleshooting steps have been performed, \nplease re-enter the API key information.")
    else:
      account_name = get_account.results[0].name
      print("Access to the Intersight API has passed.")
      print("The account named '" + account_name + "' has been found.")
      break
  except Exception:
    print("Unable to access the Intersight API.")
    print("Please verify that the API key information entered was correct.")
    print("Also check https://status.intersight.com to verify the \nIntersight service is available.\n")
    print("If the above troubleshooting steps have been performed, please re-enter the API key information.")

# Request user to input the name of the HyperFlex cluster to be monitored
while True:
  while True:
    hyperflex_cluster_answer = input("\nPlease enter the name of the HyperFlex Edge cluster you are deploying:\n")
    hyperflex_cluster = hyperflex_cluster_answer.strip()
    if len(hyperflex_cluster) is not 0: break
    print("That answer is invalid.")
  try:
    # Check for the presence of the targeted HyperFlex cluster profile
    hxcps_list = []
    print("\nSearching for the HyperFlex cluster profile named " + hyperflex_cluster + "...\n")
    check_hxcps = intersight.apis.hyperflex_cluster_profile_api.HyperflexClusterProfileApi(api_instance)
    get_hxcps = check_hxcps.hyperflex_cluster_profiles_get()
    get_hxcps_dict = get_hxcps.to_dict()
    if get_hxcps_dict["results"] is not None:
      for profile in get_hxcps_dict["results"]:
        hxcps_list.append(profile["name"])
      hxcps_list_count = len(hxcps_list)
      hxcps_list_count_string = str(hxcps_list_count)
      hxcps_list_string = str(hxcps_list).strip("[]'")
      if hyperflex_cluster in hxcps_list:
        print("The HyperFlex cluster profile named " + hyperflex_cluster + " has been found.")
        break
      else:
        print("The HyperFlex cluster profile named '" + hyperflex_cluster + "' was not found.")
        print("Other HyperFlex cluster profiles were found. The total found was " + hxcps_list_count_string + ".")
        print("Please verify the spelling or presence of the desired HyperFlex cluster \nprofile then re-enter the HyperFlex cluster profile name.")
    else:
      print("No HyperFlex cluster profiles were found.")
      print("Please create a HyperFlex cluster profile, start the deployment, \nthen re-enter the HyperFlex cluster profile name.")
  except Exception:
    print("Unable to access the Intersight API to check for the presence of the HyperFlex cluster profile named" + hyperflex_cluster + ".")
    print("Please check https://status.intersight.com to verify the \nIntersight service is available.\n")
    print("If the above troubleshooting steps have been performed, \nplease re-enter the HyperFlex cluster profile name.")

# Request the user to provide the SMTP server for sending the alerts
while True:
  while True:
    smtp_server_answer = input("\nPlease enter the IPv4 address of a reachable SMTP server \nfor sending the notification email alerts:\n")
    smtp_server = smtp_server_answer.strip()
    if len(smtp_server) is not 0 and "." in smtp_server: break
    print("That answer is invalid")

  try:
    print("\nTesting access to the SMTP server at " + smtp_server + "...\n")
    smtpserver = smtplib.SMTP(smtp_server)
    smtpserver.quit()
    print("Access to " + smtp_server + " was successful.")
    break
  except Exception:
    print("Unable to access the provided SMTP server.")
    print("Please verify and re-enter the IP address or provide a different SMTP server.")

# Request user to input the email address to receive alerts
while True:
  notification_email_answer = input("\nPlease enter the email address to receive alerts:\n")
  notification_email = notification_email_answer.strip()
  if len(notification_email) is not 0 and "@" in notification_email: break
  print("That answer is invalid.")

# Request user to set the maximum amount of warnings to be sent during session
while True:
  max_warnings_answer = input("\nPlease enter the maximum number of warnings you will accept during this session:\n[Press Enter for the default: 5]\n")
  max_warnings_stripped = max_warnings_answer.strip()
  if len(max_warnings_stripped) == 0:
    max_warnings = 5
    break
  try:
    max_warnings = int(max_warnings_stripped)
  except Exception:
    print("That answer is invalid, please enter a number greater than 0")
  if max_warnings > 0: break
  print("That answer is invalid, please enter a number greater than 0")

# Request user to set the interval for monitoring the HX cluster
while True:
  monitor_interval_answer = input("\nPlease enter the desired number of minutes between the monitoring intervals \nof your HyperFlex Edge cluster deployment:\n[Press Enter for the default: 10]\n")
  monitor_interval_stripped = monitor_interval_answer.strip()
  if len(monitor_interval_stripped) == 0:
    monitor_interval = 10
    break
  try:
    monitor_interval = int(monitor_interval_stripped)
  except Exception:
    print("That answer is invalid, please enter a number greater than or equal to 5")
  if  monitor_interval >= 5: break
  print("That answer is invalid, please enter a number greater than or equal to 5")

# Convert monitor interval minutes to seconds
monitor_interval_seconds = monitor_interval * 60

# Intersight alert functions and needed parameters

# Setup email alert sender and recipients
sender = "HX_Notification_Tool@hxnt.com"
receivers = [notification_email]

def hx_complete_alert():
  """
  Function to alert for successful HyperFlex Edge Deployment
  """
  
  # Create Email
  msg = MIMEMultipart()
  msg["From"] = sender
  msg["To"] = ", ".join(receivers)
  msg["Date"] = formatdate(localtime=True)
  msg["Subject"] = "[HX Notification Tool]: The HyperFlex Edge Cluster Deployment Has Completed Successfully"

  # Email body content
  message = """<html>
  <body>
  <b>BRIEF INFO</b>
  <br>
  <b>Alert:</b> Successful Deployment
  <br>
  <b>Targeted HX Cluster:</b> %(hyperflex_cluster)s
  <br><br>
  Hello,
  <br><br>
  The deployment for the HyperFlex Edge cluster named %(hyperflex_cluster)s has completed successfully and is now available!
  <br><br>
  Please log back into your Intersight account to access the cluster.
  <br><br>
  Thank you!
  <br>
  </body>
  </html>

  <br><br>
  """ % dict(
    date=date,
    notification_email=notification_email,
    hyperflex_cluster=hyperflex_cluster
    )

  msg.attach(MIMEText(message, "html"))

  try:
    # Set SMTP server and send email
    smtpserver = smtplib.SMTP(smtp_server)
    smtpserver.sendmail(sender, receivers, msg.as_string())
    smtpserver.quit()
    print("A notification email was succesfully sent.")
  except Exception:
    print("Unable to reach the provided SMTP server, another attempt will be made on the next monitoring interval.")


def hx_failure_alert():
  """
  Function to alert for failure during HyperFlex Edge cluster deployment
  """
  
  # Create Email
  msg = MIMEMultipart()
  msg["From"] = sender
  msg["To"] = ", ".join(receivers)
  msg["Date"] = formatdate(localtime=True)
  msg["Subject"] = "[HX Notification Tool]: A HyperFlex Edge Cluster Deployment Task Has Failed"

  # Email body content
  message = """<html>
  <body>
  <b>BRIEF INFO</b>
  <br>
  <b>Alert:</b> Deployment Failure (Alert #%(current_warnings)s)
  <br>
  <b>Targeted HX Cluster:</b> %(hyperflex_cluster)s
  <br><br>
  Hello,
  <br><br>
  A task failure has occurred during the deployment for the HyperFlex Edge cluster named %(hyperflex_cluster)s.
  <br>
  The option to retry or restart the deployment may be available. Please log back into your Intersight account to access the cluster deployment wizard.
  <br>
  Please be advised that a maximum of %(max_warnings)s warning alert emails has been set for this HX Edge deployment.
  <br><br>
  Thank you!
  <br>
  </body>
  </html>

  <br><br>
  """ % dict(
    date=date,
    notification_email=notification_email,
    hyperflex_cluster=hyperflex_cluster,
    max_warnings=max_warnings,
    current_warnings=current_warnings
    )

  msg.attach(MIMEText(message, "html"))

  try:
    # Set SMTP server and send email
    smtpserver = smtplib.SMTP(smtp_server)
    smtpserver.sendmail(sender, receivers, msg.as_string())
    smtpserver.quit()
    print("A notification email was succesfully sent.")
  except Exception:
    print("Unable to reach the provided SMTP server, another attempt will be made on the next monitoring interval.")


def hx_pending_alert():
  """
  Function to alert for pending-changes needed on HyperFlex Edge cluster deployment
  """
  
  # Create Email
  msg = MIMEMultipart()
  msg["From"] = sender
  msg["To"] = ", ".join(receivers)
  msg["Date"] = formatdate(localtime=True)
  msg["Subject"] = "[HX Notification Tool]: The HyperFlex Edge Cluster Deployment Has Pending-Changes Required"

  # Email body content
  message = """<html>
  <body>
  <b>BRIEF INFO</b>
  <br>
  <b>Alert:</b> Pending-Changes (Alert #%(current_warnings)s)
  <br>
  <b>Targeted HX Cluster:</b> %(hyperflex_cluster)s
  <br><br>
  Hello,
  <br><br>
  The deployment for the HyperFlex Edge cluster named %(hyperflex_cluster)s has pending changes that require your input.
  <br>
  Please log back into your Intersight account to access the cluster deployment wizard and address the pending-changes for the deployment to continue.
  <br>
  Please be advised that a maximum of %(max_warnings)s warning alert emails has been set for this HX Edge deployment.
  <br><br>
  Thank you!
  <br>
  </body>
  </html>

  <br><br>
  """ % dict(
    date=date,
    notification_email=notification_email,
    hyperflex_cluster=hyperflex_cluster,
    max_warnings=max_warnings,
    current_warnings=current_warnings
    )

  msg.attach(MIMEText(message, "html"))

  try:
    # Set SMTP server and send email
    smtpserver = smtplib.SMTP(smtp_server)
    smtpserver.sendmail(sender, receivers, msg.as_string())
    smtpserver.quit()
    print("A notification email was succesfully sent.")
  except Exception:
    print("Unable to reach the provided SMTP server, another attempt will be made on the next monitoring interval.")


def hx_mismatch_alert():
  """
  Function to alert for mismatched HyperFlex Edge cluster
  """
  
  # Create Email
  msg = MIMEMultipart()
  msg["From"] = sender
  msg["To"] = ", ".join(receivers)
  msg["Date"] = formatdate(localtime=True)
  msg["Subject"] = "[HX Notification Tool]: Unable to Find the Targeted HyperFlex Cluster"

  # Email body content
  message = """<html>
  <body>
  <b>BRIEF INFO</b>
  <br>
  <b>Alert:</b> Missing HyperFlex Cluster Profile (Alert #%(current_warnings)s)
  <br>
  <b>Targeted HX Cluster:</b> %(hyperflex_cluster)s
  <br><br>
  Hello,
  <br><br>
  The HyperFlex Edge cluster named %(hyperflex_cluster)s was not found under the Intersight account %(account_name)s.
  <br>
  The total number of HyperFlex cluster profiles that were found is %(hxcps_list_count_string)s.
  <br>
  Please verify the name of the HyperFlex cluster profile you need monitored and re-run the HX Notification Tool if needed.
  <br>
  Please be advised that a maximum of %(max_warnings)s warning alert emails has been set for this HX Edge deployment.
  <br><br>
  Thank you!
  <br>
  </body>
  </html>

  <br><br>
  """ % dict(
    date=date,
    notification_email=notification_email,
    hyperflex_cluster=hyperflex_cluster,
    hxcps_list_count_string=hxcps_list_count_string,
    max_warnings=max_warnings,
    current_warnings=current_warnings,
    account_name=account_name
    )

  msg.attach(MIMEText(message, "html"))

  try:
    # Set SMTP server and send email
    smtpserver = smtplib.SMTP(smtp_server)
    smtpserver.sendmail(sender, receivers, msg.as_string())
    smtpserver.quit()
    print("A notification email was succesfully sent.")
  except Exception:
    print("Unable to reach the provided SMTP server, another attempt will be made on the next monitoring interval.")


def hx_missing_alert():
  """
  Function to alert for missing HyperFlex Edge cluster
  """
  
  # Create Email
  msg = MIMEMultipart()
  msg["From"] = sender
  msg["To"] = ", ".join(receivers)
  msg["Date"] = formatdate(localtime=True)
  msg["Subject"] = "[HX Notification Tool]: No HyperFlex Clusters were Found"

  # Email body content
  message = """<html>
  <body>
  <b>BRIEF INFO</b>
  <br>
  <b>Alert:</b> Missing HyperFlex Cluster Profile (Alert #%(current_warnings)s)
  <br>
  <b>Targeted HX Cluster:</b> %(hyperflex_cluster)s
  <br><br>
  Hello,
  <br><br>
  The HyperFlex Edge cluster named %(hyperflex_cluster)s was not found under the Intersight account %(account_name)s.
  <br>
  No other HyperFlex cluster profiles were found.
  <br>
  Please create the HyperFlex cluster profile you need monitored and re-run the HX Notification Tool if needed.
  <br>
  Please be advised that a maximum of %(max_warnings)s warning alert emails has been set for this HX Edge deployment.
  <br><br>
  Thank you!
  <br>
  </body>
  </html>

  <br><br>
  """ % dict(
    date=date,
    notification_email=notification_email,
    hyperflex_cluster=hyperflex_cluster,
    max_warnings=max_warnings,
    current_warnings=current_warnings,
    account_name=account_name
    )

  msg.attach(MIMEText(message, "html"))

  try:
    # Set SMTP server and send email
    smtpserver = smtplib.SMTP(smtp_server)
    smtpserver.sendmail(sender, receivers, msg.as_string())
    smtpserver.quit()
    print("A notification email was succesfully sent.")
  except Exception:
    print("Unable to reach the provided SMTP server, another attempt will be made on the next monitoring interval.")


# Begin HyperFlex cluster monitoring session
print("\nBeginning the monitoring session:\n")

# Set current warning level
current_warnings = 0

while True:
  print("\nChecking on the status of the HyperFlex cluster profile deployment \nfor " + hyperflex_cluster + "...\n")

  # Check the status of the targeted HyperFlex cluster profile
  hxcps_list = []
  check_hxcps = intersight.apis.hyperflex_cluster_profile_api.HyperflexClusterProfileApi(api_instance)
  get_hxcps = check_hxcps.hyperflex_cluster_profiles_get()
  get_hxcps_dict = get_hxcps.to_dict()
  if get_hxcps_dict["results"] is not None:
    for profile in get_hxcps_dict["results"]:
      hxcps_list.append(profile["name"])
      if profile["name"] == hyperflex_cluster:
        target_profile_cs = profile["config_context"]["config_state"]
        target_profile_os = profile["config_context"]["oper_state"]
    hxcps_list_count = len(hxcps_list)
    hxcps_list_count_string = str(hxcps_list_count)
    hxcps_list_string = str(hxcps_list).strip("[]'")
    if hyperflex_cluster not in hxcps_list:
      print("The HyperFlex cluster profile named '" + hyperflex_cluster + "' was not found.")
      if current_warnings >= max_warnings:
        print("The maximum number of warning alerts allowed for the deployment of \nthe HyperFlex cluster named " + hyperflex_cluster + " has been reached.")
        print("No more warning alerts will be sent. Alerts for completed HyperFlex cluster profile deployments will still be sent.")
        print("\nThe next status update will be provided in " + str(monitor_interval) + " minutes...")
      else:
        print("Sending an HX deployment mismatched HyperFlex cluster profile alert to " + notification_email + "...")
        current_warnings = current_warnings + 1
        hx_mismatch_alert()
        print("The current number of warning alerts sent for the deployment of \nthe HyperFlex cluster profile named " + hyperflex_cluster + " is " + str(current_warnings) + ".")
        print("\nThe next status update will be provided in " + str(monitor_interval) + " minutes...")
  else:
    print("No HyperFlex cluster profiles were found.")
    if current_warnings >= max_warnings:
      print("The maximum number of warning alerts allowed for the deployment of \nthe HyperFlex cluster named " + hyperflex_cluster + " has been reached.")
      print("No more warning alerts will be sent. Alerts for completed HyperFlex cluster profile deployments will still be sent.")
      print("\nThe next status update will be provided in " + str(monitor_interval) + " minutes...")
    else:
      print("Sending an HX deployment missing HyperFlex cluster profile alert to " + notification_email + "...")
      current_warnings = current_warnings + 1
      hx_missing_alert()
      print("The current number of warning alerts sent for the deployment of \nthe HyperFlex cluster profile named " + hyperflex_cluster + " is " + str(current_warnings) + ".")
      print("\nThe next status update will be provided in " + str(monitor_interval) + " minutes...")

    
  # If "Pending-changes" status determined for HX cluster deployment, send pending-changes alert
  if target_profile_cs == "Pending-changes":
    print("The targeted HyperFlex cluster profile named " + hyperflex_cluster + " \nis currently in a pending-changes state.")
    if current_warnings >= max_warnings:
      print("The maximum number of warning alerts allowed for the deployment of \nthe HyperFlex cluster named " + hyperflex_cluster + " has been reached.")
      print("No more warning alerts will be sent. Alerts for completed HyperFlex cluster profile deployments will still be sent.")
      print("\nThe next status update will be provided in " + str(monitor_interval) + " minutes...")
    else:
      print("Sending an HX deployment pending-changes alert to " + notification_email + "...")
      current_warnings = current_warnings + 1
      hx_pending_alert()
      print("The current number of warning alerts sent for the deployment of \nthe HyperFlex cluster profile named " + hyperflex_cluster + " is " + str(current_warnings) + ".")
      print("\nThe next status update will be provided in " + str(monitor_interval) + " minutes...")


  # If "Failed" status determined for HX cluster deployment, send failure alert
  if target_profile_cs == "Failed":
    print("The targeted HyperFlex cluster profile named " + hyperflex_cluster + " \nis currently in a failed state.")
    if current_warnings >= max_warnings:
      print("The maximum number of warning alerts allowed for the deployment of \nthe HyperFlex cluster named " + hyperflex_cluster + " has been reached.")
      print("No more warning alerts will be sent. Alerts for completed HyperFlex cluster profile deployments will still be sent.")
      print("\nThe next status update will be provided in " + str(monitor_interval) + " minutes...")
    else:
      print("Sending an HX deployment failure alert to " + notification_email + "...")
      current_warnings = current_warnings + 1
      hx_failure_alert()
      print("The current number of warning alerts sent for the deployment of \nthe HyperFlex cluster profile named " + hyperflex_cluster + " is " + str(current_warnings) + ".")
      print("\nThe next status update will be provided in " + str(monitor_interval) + " minutes...")
    
    
  # If "Associated" status determined for HX cluster deployment, send completed alert
  if target_profile_cs == "Associated":
    print("The targeted HyperFlex cluster profile named " + hyperflex_cluster + " \nis currently in an associated state.")
    print("Sending an HX deployment completion alert to " + notification_email + "...")
    hx_complete_alert()
    print("\nThe deployment of the HyperFlex cluster profile named " + hyperflex_cluster + " has completed!")
    input("Please press Enter to close the HX Notification Tool.\n\n")
    break


  # If "Assigned" or "Not-assigned" status determined for HX cluster profile, acknowledge in console window
  if target_profile_cs in ("Assigned", "Not-assigned"):
    print("The targeted HyperFlex cluster profile named " + hyperflex_cluster + " \nis currently in a state of '" + target_profile_cs.lower() + "'.")
    print("Awaiting the initiation of a deployment to start sending alerts...")
    print("\nThe next status update will be provided in " + str(monitor_interval) + " minutes...")


  # If "Configuring" or "Validating" status determined for HX cluster profile, acknowledge in console window
  if target_profile_cs in ("Configuring", "Validating"):
    print("The targeted Hyperflex cluster profile named " + hyperflex_cluster + " \nis currently in a " + target_profile_cs.lower() + " state...")
    print("There are no alerts to be sent at this time.")
    print("\nThe next status update will be provided in " + str(monitor_interval) + " minutes...")


  # Pause until next set status update interval
  time.sleep(monitor_interval_seconds)

# Exiting the HX Notification Tool
sys.exit(0)

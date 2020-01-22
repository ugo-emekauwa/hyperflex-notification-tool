"""
HyperFlex Notification Tool (HXNT) Monitor for dCloud, v1.1
Author: Ugo Emekauwa
Contact: uemekauw@cisco.com, uemekauwa@gmail.com
Summary: The HyperFlex Notification Tool will provide email notification alerts for
          the deployment of Cisco HyperFlex Edge clusters through Cisco Intersight.
Notes: A standalone version of this tool can be found on the Cisco DevNet Code Exchange
        at https://developer.cisco.com/codeexchange/github/repo/ugo-emekauwa/hyperflex-notification-tool.
"""

# Import needed Python modules
import sys
import os
import logging
import datetime
import xml.etree.ElementTree as et
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import intersight
from intersight.intersight_api_client import IntersightApiClient

# Define time variable
get_date = datetime.datetime.now()
date = get_date.strftime("%m/%d/%Y %H:%M:%S")

# Setup Logging
logging.basicConfig(filename="c:\\dcloud\\hxnt-monitor.log", level=logging.DEBUG, format="%(asctime)s %(message)s")
logging.info("Starting Intersight Service Account Availability Test and Reset process.")

# Parse dCloud session.xml file to determine assigned HyperFlex Edge cluster and assign to variable
session_xml = et.parse("c:\\dcloud\\session.xml")

# Create needed variables from session.xml file
cluster_name = session_xml.find("devices/device/name").text
datacenter_name = session_xml.find("datacenter").text

# Parse matching cluster.xml file based on assigned HyperFlex Edge cluster
if cluster_name == "HyperFlex HX220c M5 Cluster 01":
  cluster_xml = et.parse("c:\\Scripts\\Clusters\\" + datacenter_name + "\\HyperFlex HX220c M5 Cluster 01\\XML_File\\cluster01.xml")
if cluster_name == "HyperFlex HX220c M5 Cluster 02":
  cluster_xml = et.parse("c:\\Scripts\\Clusters\\" + datacenter_name + "\\HyperFlex HX220c M5 Cluster 02\\XML_File\\cluster02.xml")
if cluster_name == "HyperFlex HX220c M5 Cluster 03":
  cluster_xml = et.parse("c:\\Scripts\\Clusters\\" + datacenter_name + "\\HyperFlex HX220c M5 Cluster 03\\XML_File\\cluster03.xml")
if cluster_name == "HyperFlex HX220c M5 Cluster 04":
  cluster_xml = et.parse("c:\\Scripts\\Clusters\\" + datacenter_name + "\\HyperFlex HX220c M5 Cluster 04\\XML_File\\cluster04.xml")

# Create needed variables from cluster.xml file
intersight_account_name = cluster_xml.find("account/intersight_account").text
intersight_account_service_type = cluster_xml.find("account/service_account_type").text
intersight_account_session = session_xml.find("id").text
intersight_account_location = cluster_xml.find("datacenter").text

# Parse hxnt_configuration.xml file from the HX Notification Tool
hxnt_configuration_xml_file = r"\\wkst1\\Share\\hxnt_configuration\\hxnt_configuration.xml"
logging.info("Verifying that the HXNT configuration file has been created on wkst1.")
if not os.path.isfile(hxnt_configuration_xml_file):
  logging.info("The HXNT configuration file has not been created yet on wkst1, exiting the HXNT Monitor.\n")
  sys.exit(0)
else:
  logging.info("An HXNT configuration file has been found on wkst1, proceeding with loading the file.")
hxnt_configuration_xml = et.parse(hxnt_configuration_xml_file)

# Create needed variables from hxnt_configuration.xml file
hxnt_name = hxnt_configuration_xml.find("name").text
hxnt_email = hxnt_configuration_xml.find("email").text
hxnt_hx_cluster_name = hxnt_configuration_xml.find("hx_cluster_name").text
hx_deployment_status = hxnt_configuration_xml.find("hx_deployment_status").text
hx_deployment_warnings = hxnt_configuration_xml.find("hx_deployment_warnings").text

# Check values in HXNT configuration files to verify current HX deployment state
if hx_deployment_status == "complete":
  logging.info("The HX deployment has already completed for the cluster " + hxnt_hx_cluster_name + ", exiting the HXNT Monitor.\n")
  sys.exit(0)

# Define Intersight SDK IntersightApiClient variables
# Tested on Cisco Intersight API Reference v1.0.9-740
key_id = cluster_xml.find("account/api_keys/key01/api_key_id").text
key = "C:\\Scripts\\Clusters\\" + datacenter_name + "\\" + cluster_name + "\\Intersight_Service_Account\\API_Keys\\key01\\SecretKey.txt"
base_url = "https://intersight.com/api/v1"
api_instance = IntersightApiClient(host=base_url,private_key=key,api_key_id=key_id)

# Intersight Alert functions and needed parameters

# Setup email alert sender and recipients
sender = "HX_Notification_Tool@dcloud.cisco.com"
receivers = [hxnt_email]

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
  <b>Targeted HX Cluster:</b> %(hxnt_hx_cluster_name)s
  <br>
  <b>dCloud Session ID:</b> %(intersight_account_session)s
  <br>
  <b>dCloud Data Center:</b> %(intersight_account_location)s
  <br><br>
  Hello %(hxnt_name)s,
  <br><br>
  The deployment for the HyperFlex Edge cluster named %(hxnt_hx_cluster_name)s has completed successfully and is now available!
  <br>
  Please log back into your dCloud session to access the cluster.
  <br><br>
  Thank you!
  <br>
  </body>
  </html>

  <br><br>
  """ % dict(
    intersight_account_service_type=intersight_account_service_type,
    intersight_account_session=intersight_account_session,
    intersight_account_location=intersight_account_location,
    date=date,
    hxnt_name=hxnt_name,
    hxnt_email=hxnt_email,
    hxnt_hx_cluster_name=hxnt_hx_cluster_name,
    hx_deployment_status=hx_deployment_status
    )

  msg.attach(MIMEText(message, "html"))

  try:
    # Set SMTP server and send email
    smtpserver = smtplib.SMTP("192.168.100.100")
    smtpserver.sendmail(sender, receivers, msg.as_string())
    smtpserver.quit()
    logging.info("A notification email was successfully sent for a completed HX deployment.")
  except Exception:
    logging.info("Unable to reach the provided SMTP server, another attempt will be made on the next monitoring interval.")


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
  <b>Alert:</b> Deployment Failure (Alert #%(updated_hx_deployment_warnings)s)
  <br>
  <b>Targeted HX Cluster:</b> %(hxnt_hx_cluster_name)s
  <br>
  <b>dCloud Session ID:</b> %(intersight_account_session)s
  <br>
  <b>dCloud Data Center:</b> %(intersight_account_location)s
  <br><br>
  Hello %(hxnt_name)s,
  <br><br>
  A task failure has occurred during the deployment for the HyperFlex Edge cluster named %(hxnt_hx_cluster_name)s.
  <br>
  The option to retry or restart the deployment may be available. Please log back into your dCloud session to access the Intersight cluster deployment wizard.
  <br>
  Please be advised that a maximum of 5 warning alert emails will be sent for this HX Edge deployment.
  <br><br>
  Thank you!
  <br>
  </body>
  </html>

  <br><br>
  """ % dict(
    intersight_account_service_type=intersight_account_service_type,
    intersight_account_session=intersight_account_session,
    intersight_account_location=intersight_account_location,
    date=date,
    hxnt_name=hxnt_name,
    hxnt_email=hxnt_email,
    hxnt_hx_cluster_name=hxnt_hx_cluster_name,
    updated_hx_deployment_warnings=updated_hx_deployment_warnings,
    hx_deployment_status=hx_deployment_status
    )

  msg.attach(MIMEText(message, "html"))

  try:
    # Set SMTP server and send email
    smtpserver = smtplib.SMTP("192.168.100.100")
    smtpserver.sendmail(sender, receivers, msg.as_string())
    smtpserver.quit()
    logging.info("A notification email was successfully sent for a task failure in an HX deployment.")
  except Exception:
    logging.info("Unable to reach the provided SMTP server, another attempt will be made on the next monitoring interval.")


def hx_pending_alert():
  """
  Function to alert for successful HyperFlex Edge cluster deployment
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
  <b>Alert:</b> Pending-Changes (Alert #%(updated_hx_deployment_warnings)s)
  <br>
  <b>Targeted HX Cluster:</b> %(hxnt_hx_cluster_name)s
  <br>
  <b>dCloud Session ID:</b> %(intersight_account_session)s
  <br>
  <b>dCloud Data Center:</b> %(intersight_account_location)s
  <br><br>
  Hello %(hxnt_name)s,
  <br><br>
  The deployment for the HyperFlex Edge cluster named %(hxnt_hx_cluster_name)s has pending changes that require your input.
  <br>
  Please log back into your dCloud session to access the Intersight cluster deployment wizard and address the pending-changes for the deployment to continue.
  <br>
  Please be advised that a maximum of 5 warning alert emails will be sent for this HX Edge deployment.
  <br><br>
  Thank you!
  <br>
  </body>
  </html>

  <br><br>
  """ % dict(
    intersight_account_service_type=intersight_account_service_type,
    intersight_account_session=intersight_account_session,
    intersight_account_location=intersight_account_location,
    date=date,
    hxnt_name=hxnt_name,
    hxnt_email=hxnt_email,
    hxnt_hx_cluster_name=hxnt_hx_cluster_name,
    updated_hx_deployment_warnings=updated_hx_deployment_warnings,
    hx_deployment_status=hx_deployment_status
    )

  msg.attach(MIMEText(message, "html"))

  try:
    # Set SMTP server and send email
    smtpserver = smtplib.SMTP("192.168.100.100")
    smtpserver.sendmail(sender, receivers, msg.as_string())
    smtpserver.quit()
    logging.info("A notification email was successfully sent for pending-changes needed in an HX deployment.")
  except Exception:
    logging.info("Unable to reach the provided SMTP server, another attempt will be made on the next monitoring interval.")


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
  <b>Alert:</b> Missing HyperFlex Cluster Profile (Alert #%(updated_hx_deployment_warnings)s)
  <br>
  <b>Targeted HX Cluster:</b> %(hxnt_hx_cluster_name)s
  <br>
  <b>dCloud Session ID:</b> %(intersight_account_session)s
  <br>
  <b>dCloud Data Center:</b> %(intersight_account_location)s
  <br><br>
  Hello %(hxnt_name)s,
  <br><br>
  The HyperFlex Edge cluster named %(hxnt_hx_cluster_name)s was not found under the dCloud Intersight account.
  <br>
  The following HyperFlex cluster profiles were found: %(hxcps_list)s.
  <br>
  Please verify the name of the HyperFlex cluster profile you need monitored and re-run the HX Notification Tool if needed.
  <br>
  Please be advised that a maximum of 5 warning alert emails will be sent for this HX Edge deployment.
  <br><br>
  Thank you!
  <br>
  </body>
  </html>

  <br><br>
  """ % dict(
    intersight_account_service_type=intersight_account_service_type,
    intersight_account_session=intersight_account_session,
    intersight_account_location=intersight_account_location,
    date=date,
    hxnt_name=hxnt_name,
    hxnt_email=hxnt_email,
    hxnt_hx_cluster_name=hxnt_hx_cluster_name,
    updated_hx_deployment_warnings=updated_hx_deployment_warnings,
    hx_deployment_status=hx_deployment_status,
    hxcps_list=hxcps_list
    )

  msg.attach(MIMEText(message, "html"))

  try:
    # Set SMTP server and send email
    smtpserver = smtplib.SMTP("192.168.100.100")
    smtpserver.sendmail(sender, receivers, msg.as_string())
    smtpserver.quit()
    logging.info("A notification email was successfully sent for a mismatched HX cluster profile name.")
  except Exception:
    logging.info("Unable to reach the provided SMTP server, another attempt will be made on the next monitoring interval.")


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
  <b>Alert:</b> Missing HyperFlex Cluster Profile (Alert #%(updated_hx_deployment_warnings)s)
  <br>
  <b>Targeted HX Cluster:</b> %(hxnt_hx_cluster_name)s
  <br>
  <b>dCloud Session ID:</b> %(intersight_account_session)s
  <br>
  <b>dCloud Data Center:</b> %(intersight_account_location)s
  <br><br>
  Hello %(hxnt_name)s,
  <br><br>
  The HyperFlex Edge cluster named %(hxnt_hx_cluster_name)s was not found under the dCloud Intersight account.
  <br>
  No other HyperFlex Cluster profiles were found.
  <br>
  Please create the HyperFlex cluster profile you need monitored and re-run the HX Notification Tool if needed.
  <br>
  Please be advised that a maximum of 5 warning alert emails will be sent for this HX Edge deployment.
  <br><br>
  Thank you!
  <br>
  </body>
  </html>

  <br><br>
  """ % dict(
    intersight_account_service_type=intersight_account_service_type,
    intersight_account_session=intersight_account_session,
    intersight_account_location=intersight_account_location,
    date=date,
    hxnt_name=hxnt_name,
    hxnt_email=hxnt_email,
    hxnt_hx_cluster_name=hxnt_hx_cluster_name,
    updated_hx_deployment_warnings=updated_hx_deployment_warnings,
    hx_deployment_status=hx_deployment_status,
    hxcps_list=hxcps_list
    )

  msg.attach(MIMEText(message, "html"))

  try:
    # Set SMTP server and send email
    smtpserver = smtplib.SMTP("192.168.100.100")
    smtpserver.sendmail(sender, receivers, msg.as_string())
    smtpserver.quit()
    logging.info("A notification email was successfully sent for a missing HX cluster profile.")
  except Exception:
    logging.info("Unable to reach the provided SMTP server, another attempt will be made on the next monitoring interval.")


def test_intersight_service():
  """
  Function to test the availability of the Intersight API
  """
  try:
    # Check that Intersight Account is accessible
    logging.info("Testing access to the Intersight API by verifying the Intersight account information...")
    check_account = intersight.apis.iam_account_api.IamAccountApi(api_instance)
    get_account = check_account.iam_accounts_get()
    if check_account.api_client.last_response.status is not 200:
      logging.info("The Intersight API Availability Test did not pass.")
      logging.info("The Intersight account information could not be verified.")
      logging.info("Another attempt to access the Intersight API will be made on the next HXNT Monitor task interval.")
      logging.info("Exiting the HXNT Monitor.\n")
      sys.exit(0)
    else:
      account_name = get_account.results[0].name
      logging.info("The Intersight API Availability Test has passed.")
      logging.info("The account named '" + intersight_account_name + "' has been found.")
  except Exception:
    logging.info("Unable to access the Intersight API.")
    logging.info("Another attempt to access the Intersight API will be made on the next HXNT Monitor task interval.")
    logging.info("Exiting the HXNT Monitor.\n")
    sys.exit(0)


def update_conf_warnings():
  """
  Functon to update the HXNT configuration file warnings value
  """
  hxnt_configuration_xml_root = hxnt_configuration_xml.getroot()
  for element in hxnt_configuration_xml_root.iter("hx_deployment_warnings"):
      element.text = str(updated_hx_deployment_warnings)
      hxnt_configuration_xml.write(hxnt_configuration_xml_file)
      logging.info("Updated the hx_deployment_warnings value in the HXNT configuration file on wkst1 to " + str(updated_hx_deployment_warnings) + ".")


# Run Intersight Service Account Availability Test
logging.info("Running Intersight API Availability Test.")
test_intersight_service()

# Check the status of the targeted HyperFlex cluster profile
hxcps_list = []
check_hxcps = intersight.apis.hyperflex_cluster_profile_api.HyperflexClusterProfileApi(api_instance)
get_hxcps = check_hxcps.hyperflex_cluster_profiles_get()
get_hxcps_dict = get_hxcps.to_dict()
if get_hxcps_dict["results"] is not None:
  logging.info:("Adding found HyperFlex cluster profiles to list.")
  for profile in get_hxcps_dict["results"]:
    hxcps_list.append(profile["name"])
    if profile["name"] == hxnt_hx_cluster_name:
      target_profile_cs = profile["config_context"]["config_state"]
      target_profile_os = profile["config_context"]["oper_state"]
  hxcps_list_count = len(hxcps_list)
  hxcps_list_count_string = str(hxcps_list_count)
  hxcps_list_string = str(hxcps_list).strip("[]'")
  logging.info("The following HyperFlex cluster profiles have been found in the list: " + hxcps_list_string + ".")
  if hxnt_hx_cluster_name not in hxcps_list:
    logging.info("The HyperFlex cluster profile named '" + hxnt_hx_cluster_name + "' was not found.")
    if int(hx_deployment_warnings) >= 5:
      logging.info("The maximum number of warning alerts allowed for the deployment of \nthe HyperFlex cluster named " + hxnt_hx_cluster_name + " has been reached.")
      logging.info("No more warning alerts will be sent. Alerts for completed HyperFlex cluster profile deployments will still be sent.")
      logging.info("Exiting the HXNT Monitor.\n")
      sys.exit(0)
    else:
      logging.info("Sending an HX deployment mismatched HyperFlex cluster profile alert to " + hxnt_email + "...")
      updated_hx_deployment_warnings = int(hx_deployment_warnings) + 1
      hx_mismatch_alert()
      logging.info("The current number of warning alerts sent for the deployment of \nthe HyperFlex cluster profile named " + hxnt_hx_cluster_name + " is " + str(updated_hx_deployment_warnings) + ".")
      update_conf_warnings()
      logging.info("Exiting the HXNT Monitor.\n")
      sys.exit(0)
else:
  logging.info("No HyperFlex cluster profiles were found.")
  if int(hx_deployment_warnings) >= 5:
    logging.info("The maximum number of warning alerts allowed for the deployment of \nthe HyperFlex cluster named " + hxnt_hx_cluster_name + " has been reached.")
    logging.info("No more warning alerts will be sent. Alerts for completed HyperFlex cluster profile deployments will still be sent.")
    logging.info("Exiting the HXNT Monitor.\n")
    sys.exit(0)
  else:
    logging.info("Sending an HX deployment missing HyperFlex cluster profile alert to " + hxnt_email + "...")
    updated_hx_deployment_warnings = int(hx_deployment_warnings) + 1
    hx_missing_alert()
    logging.info("The current number of warning alerts sent for the deployment of \nthe HyperFlex cluster profile named " + hxnt_hx_cluster_name + " is " + str(updated_hx_deployment_warnings) + ".")
    update_conf_warnings()
    logging.info("Exiting the HXNT Monitor.\n")
    sys.exit(0)

# If "Pending-changes" status determined for HX cluster deployment, send pending-changes alert
if target_profile_cs == "Pending-changes":
  logging.info("The targeted HyperFlex cluster profile named " + hxnt_hx_cluster_name + " \nis currently in a pending-changes state.")
  if int(hx_deployment_warnings) >= 5:
    logging.info("The maximum number of warning alerts allowed for the deployment of \nthe HyperFlex cluster named " + hxnt_hx_cluster_name + " has been reached.")
    logging.info("No more warning alerts will be sent. Alerts for completed HyperFlex cluster profile deployments will still be sent.")
    logging.info("Exiting the HXNT Monitor.\n")
    sys.exit(0)
  else:
    logging.info("Sending an HX deployment pending-changes alert to " + hxnt_email + "...")
    updated_hx_deployment_warnings = int(hx_deployment_warnings) + 1
    hx_pending_alert()
    logging.info("The current number of warning alerts sent for the deployment of \nthe HyperFlex cluster profile named " + hxnt_hx_cluster_name + " is " + str(updated_hx_deployment_warnings) + ".")
    hxnt_configuration_xml_root = hxnt_configuration_xml.getroot()
    update_conf_warnings()
    logging.info("Exiting the HXNT Monitor.\n")
    sys.exit(0)

# If "Failed" status determined for HX cluster deployment, send failure alert
if target_profile_cs == "Failed":
  logging.info("The targeted HyperFlex cluster profile named " + hxnt_hx_cluster_name + " \nis currently in a failed state.")
  if int(hx_deployment_warnings) >= 5:
    logging.info("The maximum number of warning alerts allowed for the deployment of \nthe HyperFlex cluster named " + hxnt_hx_cluster_name + " has been reached.")
    logging.info("No more warning alerts will be sent. Alerts for completed HyperFlex cluster profile deployments will still be sent.")
    logging.info("Exiting the HXNT Monitor.\n")
    sys.exit(0)
  else:
    logging.info("Sending an HX deployment failure alert to " + hxnt_email + "...")
    updated_hx_deployment_warnings = int(hx_deployment_warnings) + 1
    hx_failure_alert()
    logging.info("The current number of warning alerts sent for the deployment of \nthe HyperFlex cluster profile named " + hxnt_hx_cluster_name + " is " + str(updated_hx_deployment_warnings) + ".")
    hxnt_configuration_xml_root = hxnt_configuration_xml.getroot()
    update_conf_warnings()
    logging.info("Exiting the HXNT Monitor.\n")
    sys.exit(0)
  
# If "Associated" status determined for HX cluster deployment, send completed alert
if target_profile_cs == "Associated":
  logging.info("The targeted HyperFlex cluster profile named " + hxnt_hx_cluster_name + " \nis currently in an associated state.")
  logging.info("Sending an HX deployment completion alert to " + hxnt_email + "...")
  hx_complete_alert()
  logging.info("\nThe deployment of the HyperFlex cluster profile named " + hxnt_hx_cluster_name + " has completed!")
  hxnt_configuration_xml_root = hxnt_configuration_xml.getroot()
  for element in hxnt_configuration_xml_root.iter("hx_deployment_status"):
    element.text = "complete"
    hxnt_configuration_xml.write(hxnt_configuration_xml_file)
    logging.info("Updated the HXNT configuration file on wkst1 to indicate the HX deployment has succesfully completed.")
  logging.info("Exiting the HXNT Monitor.\n")
  sys.exit(0)

# If "Assigned" or "Not-assigned" status determined for HX cluster profile, acknowledge in console window
if target_profile_cs in ("Assigned", "Not-assigned"):
  logging.info("The targeted HyperFlex cluster profile named " + hxnt_hx_cluster_name + " \nis currently in a state of '" + target_profile_cs.lower() + "'.")
  logging.info("Awaiting the initiation of a deployment to start sending alerts...")
  logging.info("Exiting the HXNT Monitor.\n")
  sys.exit(0)

# If "Configuring" or "Validating" status determined for HX cluster profile, acknowledge in console window
if target_profile_cs in ("Configuring", "Validating"):
  logging.info("The targeted Hyperflex cluster profile named " + hxnt_hx_cluster_name + " \nis currently in a " + target_profile_cs.lower() + " state...")
  logging.info("There are no alerts to be sent at this time.")
  logging.info("Exiting the HXNT Monitor.\n")
  sys.exit(0)

# Exiting the HX Notification Tool Monitor
sys.exit(0)

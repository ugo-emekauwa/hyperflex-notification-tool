"""
HyperFlex Notification Tool (HXNT) Configurator for dCloud, v1.0
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
import time
import datetime
import xml.etree.ElementTree as et
import shutil


# Define time variable
get_date = datetime.datetime.now()
date = get_date.strftime("%m/%d/%Y %H:%M:%S")

# Setup Logging
logging.basicConfig(filename="c:\\dcloud\\hxnt-configurator.log", level=logging.DEBUG, format="%(asctime)s %(message)s")
logging.info("Starting Notification Tool Configuration process.\n")

# Parse dCloud session.xml file to determine assigned HyperFlex Edge cluster and assign to variable
session_xml = et.parse("c:\\dcloud\\session.xml")

# Create needed variables from session.xml file
intersight_account_session = session_xml.find("id").text
session_owner = session_xml.find("owner").text

# HyperFlex Edge Notification Tool Banner and Greeting

print("                       < HX Notification Tool for dCloud >\n\n")
print("Hello " + session_owner + "!\n")
print("The HX Notification Tool will send email notifications \non the status of your HyperFlex Edge cluster deployment.\n")
hyperflex_cluster_answer = input("Please enter the name of the HyperFlex Edge cluster you are deploying: \n[dcloud-hx-edge-cluster-1]\n")
hyperflex_cluster = hyperflex_cluster_answer.strip()
if len(hyperflex_cluster) == 0:
  hyperflex_cluster = "dcloud-hx-edge-cluster-1"
while True:
  notification_email_answer = input("Please enter the email address to receive alerts:\n")
  notification_email = notification_email_answer.strip()
  if len(notification_email) is not 0 and "@" in notification_email: break
  print("That answer is invalid.")
  

# Set HX Notification Tool configuration folder path variable
path = "c:\\Share\\hxnt_configuration"
logging.info("Setting HX Notification Tool configuration folder path variable.")

# Delete configuration folder if it exists
try:
  shutil.rmtree(path)
  logging.info("The HX Notification Tool configuration folder has been deleted for reset purposes.")
except Exception as exception_message:
  logging.info("Unable to delete the HX Notification Tool configuration folder")
  logging.info(exception_message)

# Create folder for configuration file
time.sleep(2)
if not os.path.exists(path):
  os.makedirs(path)
  logging.info("The folder '" + path + "' has been created.")
else:
  logging.info("Unable to create the folder '" + path + "'.")
  
# Create configuration XML file
try:
  hxnt_configuration = et.Element("hxnt_configuration")
  name = et.SubElement(hxnt_configuration, "name")
  email = et.SubElement(hxnt_configuration, "email")
  hx_cluster_name = et.SubElement(hxnt_configuration, "hx_cluster_name")
  hx_deployment_warnings = et.SubElement(hxnt_configuration, "hx_deployment_warnings")
  hx_deployment_status = et.SubElement(hxnt_configuration, "hx_deployment_status")
  name.text = session_owner
  email.text = notification_email
  hx_cluster_name.text = hyperflex_cluster
  hx_deployment_warnings.text = "0"
  hx_deployment_status.text = "incomplete"
  hx_configuration_xml = et.ElementTree(hxnt_configuration)
  hx_configuration_xml.write("c:\\Share\\hxnt_configuration\\hxnt_configuration.xml")
  logging.info("The HX Notification Tool configuration XML file has been created.\n")
  print("\n\nThank you " + session_owner + ".\n")
  print("The HyperFlex Edge cluster to be monitored is named:\n '" + hyperflex_cluster + "'\n")
  print("The notification emails will be sent to:\n '" + notification_email + "'\n")
  print("Please re-run the HX Notification Tool if the name of the HyperFlex \nEdge cluster and/or the email address listed above are incorrect.\n")
  print("Otherwise, please press Enter to close the HX Notification Tool window.\n\n")
  input("A standalone version of this tool can be found on the Cisco DevNet Code Exchange at \nhttps://developer.cisco.com/codeexchange/github/repo/ugo-emekauwa/hyperflex-notification-tool\n\n")
except Exception as exception_message:
  logging.info("Unable to complete creating the HX Notification Tool configuration XML file")
  logging.info(exception_message + "\n")
  print("\nAcceptance of the data entered for the HX Notification Tool has failed.")
  print("The configuration folder may be opened or in use.")
  print("Please close the configuration folder if it is opened.\n")
  print("Please, press Enter to close the HX Notification Tool and attempt to re-run it.\n")
  input("A standalone version of this tool can be found on the Cisco DevNet Code Exchange at \nhttps://developer.cisco.com/codeexchange/github/repo/ugo-emekauwa/hyperflex-notification-tool\n\n")


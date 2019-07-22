# HyperFlex Notification Tool for Cisco Intersight

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/ugo-emekauwa/hyperflex-notification-tool)

The HyperFlex Notification Tool (HXNT) provides email alert notifications on the status of Cisco HyperFlex Edge cluster deployments through Cisco Intersight.
No longer do you have to manually check or monitor the Intersight web interface to find out the status of your deployments.
HXNT will automatically provide updates on HyperFlex deployment completions, task failures, required pending changes, and missing HyperFlex cluster profiles.

## Prerequisites:
  1. Python 3 installed, which can be downloaded from [https://www.python.org/downloads/](https://www.python.org/downloads/).
  2. The Cisco Intersight SDK for Python, which can be installed by running:
     ```py
     pip install git+https://github.com/CiscoUcs/intersight-python.git
     ```
     More information on the Cisco Intersight SDK for Python can be found at [https://github.com/CiscoUcs/intersight-python](https://github.com/CiscoUcs/intersight-python).
  3. An API key from your Intersight account. To learn how to generate an API key for your Intersight account, more information can be found at [https://intersight.com/help/features#rest_apis](https://intersight.com/help/features#rest_apis).
  4. A reachable SMTP server.

## Getting Started:

  1. Please ensure that the above prerequisites have been met.
  2. Download the hxnt_standalone.py file for the HyperFlex Notification Tool from here on GitHub.
  3. Create a HyperFlex cluster profile on Cisco Intersight and begin the validation and deployment.
  4. Run the hxnt_standalone.py file.


The HyperFlex Notification Tool is completely interactive and will prompt you for the information needed to begin monitoring the status of your HyperFlex deployment.
The HyperFlex Notification Tool can also be easily scripted if desired for scenarios where several HyperFlex clusters are being deployed simultaneously. Please see the contact information below if any help is needed or questions.

## Use Cases:
- A modified version of the Hyperflex Notification Tool has been built for Cisco dCloud and is featured in the demonstration named **_Cisco HyperFlex Edge with Intersight v1_**, available at [https://dcloud-cms.cisco.com/demo/cisco-hyperflex-edge-with-intersight-v1](https://dcloud-cms.cisco.com/demo/cisco-hyperflex-edge-with-intersight-v1).

## Author:
Ugo Emekauwa

## Contact Information:
uemekauw@cisco.com or uemekauwa@gmail.com

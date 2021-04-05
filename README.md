# HyperFlex Notification Tool for Cisco Intersight

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/ugo-emekauwa/hyperflex-notification-tool)

The HyperFlex Notification Tool (HXNT) provides email alert notifications on the status of Cisco HyperFlex Edge cluster deployments through Cisco Intersight.
No longer do you have to manually check or monitor the Intersight web interface to find out the status of your deployments.
HXNT will automatically provide updates on HyperFlex deployment completions, task failures, required pending changes, and missing HyperFlex cluster profiles.

## Prerequisites:
  1. Python 3 installed, which can be downloaded from [https://www.python.org/downloads/](https://www.python.org/downloads/).
  2. The Cisco Intersight SDK for Python, which can be installed by running:
     ```python
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
A modified version of the Hyperflex Notification Tool for Cisco Intersight is featured on Cisco dCloud in the following labs:

1. [_Cisco HyperFlex Edge 4.5 with Intersight v1 (All Flash, 2-Node)_](https://dcloud2-rtp.cisco.com/content/demo/760975)
2. [_Cisco HyperFlex Edge 4.5 with Intersight v1 (Hybrid, 2-Node)_](https://dcloud2-rtp.cisco.com/content/demo/760974)
3. [_Cisco HyperFlex Edge 4.5 with Intersight v1 (All Flash, 3-Node)_](https://dcloud-cms.cisco.com/demo/cisco-hyperflex-edge-4-5-with-intersight-v1-all-flash-3-node)

Cisco dCloud is available at [https://dcloud.cisco.com](https://dcloud.cisco.com), where product demonstrations and labs can be found in the Catalog.

## Related Tools:
Here are similar tools to help administer and manage Cisco HyperFlex environments.
- [HyperFlex Edge Automated Deployment Tool for Cisco Intersight](https://github.com/ugo-emekauwa/hx-auto-deploy)
- [Cisco HyperFlex API Token Manager](https://github.com/ugo-emekauwa/hx-api-token-manager)
- [HyperFlex HTML Plug-In Automated Installer](https://github.com/ugo-emekauwa/hx-html-plugin-auto-installer)

## Author:
Ugo Emekauwa

## Contact Information:
uemekauw@cisco.com or uemekauwa@gmail.com

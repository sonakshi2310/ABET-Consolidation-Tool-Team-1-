#Import
import os
import smtplib #for email sending
from email.message import EmailMessage
import difflib
from dotenv import load_dotenv
load_dotenv()

#SendGrid import (demo purpose)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

#Import Canvas API related modules if needed
import requests
import sys

#Configurations of the two files to compare
OLD_FILE_CS = "src/cs_criteria.txt"
NEW_FILE_CS = "src/new_cs_criteria.txt"

def diff_files(old_file_path: str, new_file_path: str) -> None:
    #check files existencies
    if not os.path.exists(old_file_path):
        print(f"{old_file_path} does not exist. Creating a new one.")
        exit(1)

    if not os.path.exists(new_file_path):
        print(f"{new_file_path} does not exist. Creating a new one.")
        exit(1)

    with open(old_file_path, 'r') as old_file_cs, open(new_file_path, 'r') as new_file_cs:
        old_data_cs = old_file_cs.readlines()
        new_data_cs = new_file_cs.readlines()

    # Generate diff
    diff_cs = difflib.unified_diff(old_data_cs, new_data_cs, fromfile='Old CS Criteria', tofile='New CS Criteria', lineterm='')

    if diff_cs:
        #demo print diff
        diff_text = ''.join(diff_cs)
        print("Differences found:")
        print(diff_text)
        

        #Prepare email demonstration 
        message = Mail(
            from_email=os.getenv("EMAIL_SENDER"),
            to_emails=os.getenv("EMAIL_RECEIVER"),
            subject="CS Datafile Changes Detected",
            plain_text_content=f"The following changes were detected between the old and new CS data files:\n\n{diff_text}"
        )

        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        try:
            response = sg.send(message)
            print(f"Email sent with status code {response.status_code}")
        except Exception as e:
            print(f"Error sending email: {e}")

if __name__ == '__main__':
    """
    Example test function to demonstrate diff_files().
    Update the paths below to your actual C# file locations.
    """
    diff_files(OLD_FILE_CS, NEW_FILE_CS)


#How to use:
#Set up .env file with necessary info (see .env file for reference)
#Create SendGrid account and get API key

#What to do:
#Change SendGrid account to using ASU email address
#Update the contect of the old_datafile.txt with the content of current CS_datafile.txt after verifying the changes
#The new CS_datafile.txt should from the most recent data (run ABET_CS.ipynb) while the oldCS_datafile.txt should be downloaded from the Canvas and should be replaced if there is difference detected
#Automate this script to run at desired intervals - currently manual run but desired to be weekly or monthly
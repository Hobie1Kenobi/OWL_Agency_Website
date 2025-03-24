#!/usr/bin/env python
# Directory Submission Assistant for OWL AI Agency
# This script helps track and manage legal directory submissions

import os
import csv
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import webbrowser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DirectorySubmissionAssistant:
    def __init__(self):
        self.tracker_file = "directory_submission_tracker.csv"
        self.templates_dir = "directory_submission_templates"
        self.email_notifications = True
        self.email_address = os.getenv("EMAIL_ADDRESS", "notifications@owl-ai-agency.com")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        
        # Create templates directory if it doesn't exist
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
    
    def load_tracker(self):
        """Load the directory submission tracker CSV file"""
        if os.path.exists(self.tracker_file):
            return pd.read_csv(self.tracker_file)
        else:
            # Create a new tracker file with default columns
            df = pd.DataFrame(columns=[
                "Directory", "URL", "Submission Date", "Status", 
                "Follow-up Date", "Notes"
            ])
            df.to_csv(self.tracker_file, index=False)
            return df
    
    def save_tracker(self, df):
        """Save the directory submission tracker CSV file"""
        df.to_csv(self.tracker_file, index=False)
        print(f"Tracker saved to {self.tracker_file}")
    
    def add_submission(self, directory, url, submission_date=None, status="Planned", notes=""):
        """Add a new directory submission to the tracker"""
        if submission_date is None:
            submission_date = datetime.now().strftime("%Y-%m-%d")
        
        df = self.load_tracker()
        
        # Check if directory already exists
        if directory in df["Directory"].values:
            print(f"Directory {directory} already exists in tracker. Updating...")
            df.loc[df["Directory"] == directory, "URL"] = url
            df.loc[df["Directory"] == directory, "Submission Date"] = submission_date
            df.loc[df["Directory"] == directory, "Status"] = status
            df.loc[df["Directory"] == directory, "Notes"] = notes
        else:
            # Add new row
            new_row = {
                "Directory": directory,
                "URL": url,
                "Submission Date": submission_date,
                "Status": status,
                "Follow-up Date": "",
                "Notes": notes
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        self.save_tracker(df)
        print(f"Added submission for {directory}")
    
    def update_status(self, directory, status, notes=None):
        """Update the status of a directory submission"""
        df = self.load_tracker()
        
        if directory not in df["Directory"].values:
            print(f"Directory {directory} not found in tracker")
            return
        
        df.loc[df["Directory"] == directory, "Status"] = status
        
        if notes:
            df.loc[df["Directory"] == directory, "Notes"] = notes
        
        # If status is "Submitted", set follow-up date to 7 days from now
        if status == "Submitted":
            follow_up = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            df.loc[df["Directory"] == directory, "Follow-up Date"] = follow_up
        
        # If status is "Verified" or "Rejected", clear follow-up date
        if status in ["Verified", "Rejected"]:
            df.loc[df["Directory"] == directory, "Follow-up Date"] = ""
        
        self.save_tracker(df)
        print(f"Updated status for {directory} to {status}")
    
    def get_pending_submissions(self):
        """Get list of directories with 'Planned' status"""
        df = self.load_tracker()
        return df[df["Status"] == "Planned"]
    
    def get_follow_ups_needed(self):
        """Get list of directories that need follow-up"""
        df = self.load_tracker()
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Filter for rows with follow-up date <= today and status = "Submitted"
        follow_ups = df[(df["Follow-up Date"] <= today) & 
                         (df["Follow-up Date"] != "") & 
                         (df["Status"] == "Submitted")]
        
        return follow_ups
    
    def open_submission_page(self, directory):
        """Open the submission page for a directory in the default browser"""
        df = self.load_tracker()
        
        if directory not in df["Directory"].values:
            print(f"Directory {directory} not found in tracker")
            return
        
        url = df.loc[df["Directory"] == directory, "URL"].values[0]
        print(f"Opening {url} in browser...")
        webbrowser.open(url)
    
    def load_template(self, directory):
        """Load the submission template for a directory"""
        template_file = os.path.join(self.templates_dir, f"{directory.lower()}_submission.md")
        
        if not os.path.exists(template_file):
            print(f"Template for {directory} not found")
            return None
        
        with open(template_file, "r") as f:
            template = f.read()
        
        return template
    
    def send_email_notification(self, subject, body):
        """Send email notification"""
        if not self.email_notifications or not self.email_password:
            print("Email notifications disabled or password not set")
            return
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_address
            msg["To"] = self.email_address
            msg["Subject"] = subject
            
            msg.attach(MIMEText(body, "plain"))
            
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print(f"Email notification sent: {subject}")
        except Exception as e:
            print(f"Error sending email: {e}")
    
    def generate_daily_report(self):
        """Generate a daily report of submission status"""
        df = self.load_tracker()
        
        # Count submissions by status
        status_counts = df["Status"].value_counts().to_dict()
        
        # Get pending follow-ups
        follow_ups = self.get_follow_ups_needed()
        
        # Generate report
        report = f"Directory Submission Status Report - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        report += "Status Summary:\n"
        
        for status, count in status_counts.items():
            report += f"- {status}: {count}\n"
        
        report += f"\nPending Follow-ups ({len(follow_ups)}):\n"
        
        for _, row in follow_ups.iterrows():
            report += f"- {row['Directory']} (Submitted on {row['Submission Date']})\n"
        
        report += "\nRecent Submissions:\n"
        recent = df[df["Submission Date"] >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")]
        
        for _, row in recent.iterrows():
            report += f"- {row['Directory']} ({row['Status']} on {row['Submission Date']})\n"
        
        # Save report
        report_file = f"directory_report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_file, "w") as f:
            f.write(report)
        
        print(f"Report generated: {report_file}")
        
        # Send email notification
        if self.email_notifications:
            self.send_email_notification(
                "Directory Submission Status Report",
                report
            )
        
        return report
    
    def run_interactive(self):
        """Run the assistant in interactive mode"""
        print("Directory Submission Assistant for OWL AI Agency")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. View all submissions")
            print("2. Add new submission")
            print("3. Update submission status")
            print("4. View pending submissions")
            print("5. View follow-ups needed")
            print("6. Open submission page in browser")
            print("7. View submission template")
            print("8. Generate status report")
            print("9. Exit")
            
            choice = input("\nEnter choice (1-9): ")
            
            if choice == "1":
                df = self.load_tracker()
                print("\nAll Submissions:")
                print(df.to_string())
            
            elif choice == "2":
                directory = input("Directory name: ")
                url = input("Submission URL: ")
                status = input("Status (Planned/Submitted/Verified/Rejected): ")
                notes = input("Notes: ")
                
                self.add_submission(directory, url, status=status, notes=notes)
            
            elif choice == "3":
                df = self.load_tracker()
                print("\nCurrent Submissions:")
                for i, row in df.iterrows():
                    print(f"{i+1}. {row['Directory']} - {row['Status']}")
                
                idx = int(input("\nEnter submission number to update: ")) - 1
                if 0 <= idx < len(df):
                    directory = df.iloc[idx]["Directory"]
                    status = input("New status (Planned/Submitted/Verified/Rejected): ")
                    notes = input("Notes: ")
                    
                    self.update_status(directory, status, notes)
                else:
                    print("Invalid selection")
            
            elif choice == "4":
                pending = self.get_pending_submissions()
                print("\nPending Submissions:")
                print(pending.to_string())
            
            elif choice == "5":
                follow_ups = self.get_follow_ups_needed()
                print("\nFollow-ups Needed:")
                print(follow_ups.to_string())
            
            elif choice == "6":
                df = self.load_tracker()
                print("\nDirectories:")
                for i, row in df.iterrows():
                    print(f"{i+1}. {row['Directory']}")
                
                idx = int(input("\nEnter directory number to open: ")) - 1
                if 0 <= idx < len(df):
                    directory = df.iloc[idx]["Directory"]
                    self.open_submission_page(directory)
                else:
                    print("Invalid selection")
            
            elif choice == "7":
                directory = input("Directory name: ")
                template = self.load_template(directory)
                
                if template:
                    print("\nTemplate:")
                    print(template)
            
            elif choice == "8":
                report = self.generate_daily_report()
                print("\nReport:")
                print(report)
            
            elif choice == "9":
                print("Exiting...")
                break
            
            else:
                print("Invalid choice")

if __name__ == "__main__":
    assistant = DirectorySubmissionAssistant()
    assistant.run_interactive()

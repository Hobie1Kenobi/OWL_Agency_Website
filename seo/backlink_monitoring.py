#!/usr/bin/env python
# Backlink Monitoring Script for OWL AI Agency
# This script tracks backlinks from legal directories and generates reports

import os
import requests
import pandas as pd
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BacklinkMonitor:
    def __init__(self):
        self.website_url = "owl-ai-agency.com"
        self.directories = [
            {"name": "Avvo", "url": "avvo.com", "tier": 1},
            {"name": "FindLaw", "url": "findlaw.com", "tier": 1},
            {"name": "Justia", "url": "justia.com", "tier": 1},
            {"name": "HG.org", "url": "hg.org", "tier": 2},
            {"name": "Martindale", "url": "martindale.com", "tier": 2},
            {"name": "Nolo", "url": "nolo.com", "tier": 2},
            {"name": "LawLink", "url": "lawlink.com", "tier": 2},
            {"name": "Lawyer.com", "url": "lawyer.com", "tier": 2},
            {"name": "LegalMatch", "url": "legalmatch.com", "tier": 2},
            {"name": "Priori Legal", "url": "priorilegal.com", "tier": 2},
            {"name": "Legal Tech Directory", "url": "legaltechdirectory.com", "tier": 3},
            {"name": "Stanford CodeX", "url": "techindex.law.stanford.edu", "tier": 3},
            {"name": "Legal IT Professionals", "url": "legalitprofessionals.com", "tier": 3},
            {"name": "Legal IT Insider", "url": "legaltechnology.com", "tier": 3},
            {"name": "ILTA", "url": "iltanet.org", "tier": 3}
        ]
        self.report_dir = "reports"
        
        # Create reports directory if it doesn't exist
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
    
    def check_backlink(self, directory):
        """Check if a directory contains a backlink to our website"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            # First try a Google search to find our listing
            search_url = f"https://www.google.com/search?q=site:{directory['url']}+{self.website_url}"
            response = requests.get(search_url, headers=headers)
            
            if self.website_url in response.text:
                # Found a potential match, now try to get the actual URL
                soup = BeautifulSoup(response.text, 'html.parser')
                results = soup.find_all('a')
                
                for result in results:
                    href = result.get('href', '')
                    if 'url=' in href and directory['url'] in href:
                        # Extract the actual URL
                        actual_url = href.split('url=')[1].split('&')[0]
                        
                        # Visit the page to check if it contains our link
                        try:
                            page_response = requests.get(actual_url, headers=headers, timeout=10)
                            return self.website_url in page_response.text
                        except:
                            # If we can't visit the page, assume it's a match from Google
                            return True
            
            return False
        except Exception as e:
            print(f"Error checking backlink for {directory['name']}: {e}")
            return None
    
    def check_all_backlinks(self):
        """Check backlinks from all directories"""
        results = []
        
        for directory in self.directories:
            print(f"Checking backlink from {directory['name']}...")
            has_backlink = self.check_backlink(directory)
            
            results.append({
                "directory": directory['name'],
                "url": directory['url'],
                "tier": directory['tier'],
                "has_backlink": has_backlink,
                "check_date": datetime.now().strftime("%Y-%m-%d")
            })
            
            # Avoid rate limiting
            time.sleep(2)
        
        # Save results
        df = pd.DataFrame(results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        df.to_csv(f"{self.report_dir}/backlink_check_{timestamp}.csv", index=False)
        
        return df
    
    def load_previous_checks(self):
        """Load previous backlink check results"""
        # Find the most recent backlink check file
        files = [f for f in os.listdir(self.report_dir) if f.startswith("backlink_check_")]
        
        if not files:
            return None
        
        # Sort by timestamp
        files.sort(reverse=True)
        latest_file = os.path.join(self.report_dir, files[0])
        
        # Load the file
        return pd.read_csv(latest_file)
    
    def compare_with_previous(self, current_df):
        """Compare current backlink check with previous check"""
        previous_df = self.load_previous_checks()
        
        if previous_df is None:
            print("No previous backlink check found")
            return None
        
        # Merge the dataframes
        merged_df = pd.merge(
            current_df,
            previous_df[["directory", "has_backlink"]],
            on="directory",
            how="left",
            suffixes=("_current", "_previous")
        )
        
        # Find new backlinks
        new_backlinks = merged_df[
            (merged_df["has_backlink_current"] == True) & 
            (merged_df["has_backlink_previous"] != True)
        ]
        
        # Find lost backlinks
        lost_backlinks = merged_df[
            (merged_df["has_backlink_current"] != True) & 
            (merged_df["has_backlink_previous"] == True)
        ]
        
        return {
            "new_backlinks": new_backlinks,
            "lost_backlinks": lost_backlinks
        }
    
    def generate_backlink_report(self):
        """Generate a comprehensive backlink report"""
        print("Generating backlink report...")
        
        # Check current backlinks
        current_df = self.check_all_backlinks()
        
        # Compare with previous check
        comparison = self.compare_with_previous(current_df)
        
        # Generate summary statistics
        total_backlinks = sum(current_df["has_backlink"] == True)
        tier1_backlinks = sum((current_df["tier"] == 1) & (current_df["has_backlink"] == True))
        tier2_backlinks = sum((current_df["tier"] == 2) & (current_df["has_backlink"] == True))
        tier3_backlinks = sum((current_df["tier"] == 3) & (current_df["has_backlink"] == True))
        
        # Create report
        report = {
            "timestamp": datetime.now().isoformat(),
            "website": self.website_url,
            "total_backlinks": total_backlinks,
            "tier1_backlinks": tier1_backlinks,
            "tier2_backlinks": tier2_backlinks,
            "tier3_backlinks": tier3_backlinks,
            "backlink_details": current_df.to_dict(orient="records")
        }
        
        if comparison:
            report["new_backlinks"] = len(comparison["new_backlinks"])
            report["lost_backlinks"] = len(comparison["lost_backlinks"])
            report["new_backlink_details"] = comparison["new_backlinks"].to_dict(orient="records")
            report["lost_backlink_details"] = comparison["lost_backlinks"].to_dict(orient="records")
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"{self.report_dir}/backlink_report_{timestamp}.json", 'w') as f:
            json.dump(report, f, indent=4)
        
        # Generate visualizations
        self.generate_visualizations(current_df, timestamp)
        
        print(f"Backlink report generated: backlink_report_{timestamp}.json")
        return report
    
    def generate_visualizations(self, df, timestamp):
        """Generate visualizations for the backlink report"""
        # Set the style
        sns.set(style="whitegrid")
        
        # Create a figure with multiple subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Backlinks by tier
        tier_counts = df[df["has_backlink"] == True].groupby("tier").size().reset_index(name="count")
        sns.barplot(x="tier", y="count", data=tier_counts, ax=ax1, palette="viridis")
        ax1.set_title("Backlinks by Tier")
        ax1.set_xlabel("Tier")
        ax1.set_ylabel("Number of Backlinks")
        
        # Plot 2: Backlink status by directory
        status_data = df.copy()
        status_data["status"] = status_data["has_backlink"].map({True: "Active", False: "Missing", None: "Error"})
        sns.countplot(y="directory", hue="status", data=status_data, ax=ax2, palette="viridis")
        ax2.set_title("Backlink Status by Directory")
        ax2.set_xlabel("Count")
        ax2.set_ylabel("Directory")
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(f"{self.report_dir}/backlink_visualization_{timestamp}.png")
        plt.close()
    
    def generate_historical_trend(self):
        """Generate historical trend of backlinks over time"""
        # Find all backlink check files
        files = [f for f in os.listdir(self.report_dir) if f.startswith("backlink_check_")]
        
        if len(files) < 2:
            print("Not enough historical data for trend analysis")
            return
        
        # Sort by timestamp
        files.sort()
        
        # Load all files and extract date and backlink count
        trend_data = []
        
        for file in files:
            df = pd.read_csv(os.path.join(self.report_dir, file))
            date = file.split("_")[2][:8]  # Extract date from filename
            count = sum(df["has_backlink"] == True)
            
            trend_data.append({
                "date": date,
                "backlinks": count
            })
        
        # Create dataframe and plot
        trend_df = pd.DataFrame(trend_data)
        trend_df["date"] = pd.to_datetime(trend_df["date"], format="%Y%m%d")
        
        plt.figure(figsize=(12, 6))
        sns.lineplot(x="date", y="backlinks", data=trend_df, marker="o")
        plt.title("Backlink Growth Over Time")
        plt.xlabel("Date")
        plt.ylabel("Number of Backlinks")
        plt.grid(True)
        
        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(f"{self.report_dir}/backlink_trend_{timestamp}.png")
        plt.close()
        
        print(f"Historical trend generated: backlink_trend_{timestamp}.png")

if __name__ == "__main__":
    print("Starting Backlink Monitor...")
    monitor = BacklinkMonitor()
    
    # Generate backlink report
    monitor.generate_backlink_report()
    
    # Generate historical trend if enough data
    monitor.generate_historical_trend()

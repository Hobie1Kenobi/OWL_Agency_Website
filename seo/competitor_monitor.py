#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OWL AI Agency Competitor Monitor
--------------------------------
A tool for monitoring competitor rankings, content strategies, and backlink profiles
to gain insights for SEO optimization.
"""

import os
import json
import time
import datetime
import requests
import csv
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd
import schedule

# Configuration
CONFIG = {
    "target_keywords": [
        "legal research automation",
        "batch processing legal research",
        "AI legal research",
        "legal document automation",
        "legal tech innovation"
    ],
    "competitors": [
        "lexisnexis.com",
        "thomsonreuters.com",
        "casetext.com",
        "rossintelligence.com",
        "clio.com"
    ],
    "serp_api_key": os.environ.get("SERP_API_KEY", ""),
    "output_directory": "competitor_data",
    "check_frequency_hours": 24
}

class CompetitorMonitor:
    """Monitor competitor rankings, content, and backlinks."""
    
    def __init__(self, config=None):
        """Initialize the CompetitorMonitor with configuration."""
        self.config = config or CONFIG
        self.data_dir = self.config["output_directory"]
        os.makedirs(self.data_dir, exist_ok=True)
    
    def check_serp_rankings(self, keyword, num_results=100):
        """
        Check search engine rankings for a specific keyword.
        
        Args:
            keyword (str): The keyword to check
            num_results (int): Number of results to retrieve
            
        Returns:
            dict: Ranking data for the keyword
        """
        if not self.config["serp_api_key"]:
            print(f"Warning: SERP API key not set. Using sample data for '{keyword}'.")
            return self._get_sample_rankings(keyword)
        
        # Use SerpAPI to get real SERP data
        params = {
            "q": keyword,
            "num": num_results,
            "api_key": self.config["serp_api_key"]
        }
        
        try:
            response = requests.get(
                "https://serpapi.com/search", 
                params=params,
                timeout=30
            )
            data = response.json()
            
            # Process the results
            rankings = self._process_serp_results(data, keyword)
            return rankings
            
        except Exception as e:
            print(f"Error checking rankings for '{keyword}': {e}")
            return self._get_sample_rankings(keyword)
    
    def _process_serp_results(self, data, keyword):
        """Process SERP API results into a structured format."""
        results = []
        
        # Process organic results
        organic_results = data.get("organic_results", [])
        for position, result in enumerate(organic_results, 1):
            domain = urlparse(result.get("link", "")).netloc
            
            # Check if this is a competitor or our own site
            is_competitor = any(comp in domain for comp in self.config["competitors"])
            is_own_site = "owl-ai-agency.com" in domain
            
            if is_competitor or is_own_site:
                results.append({
                    "keyword": keyword,
                    "position": position,
                    "domain": domain,
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "url": result.get("link", ""),
                    "is_competitor": is_competitor,
                    "is_own_site": is_own_site,
                    "date_checked": datetime.datetime.now().isoformat()
                })
        
        # Process featured snippets, if any
        if "answer_box" in data:
            answer_box = data["answer_box"]
            domain = urlparse(answer_box.get("link", "")).netloc
            
            is_competitor = any(comp in domain for comp in self.config["competitors"])
            is_own_site = "owl-ai-agency.com" in domain
            
            if is_competitor or is_own_site:
                results.append({
                    "keyword": keyword,
                    "position": 0,  # 0 indicates featured snippet
                    "domain": domain,
                    "title": answer_box.get("title", ""),
                    "snippet": answer_box.get("snippet", ""),
                    "url": answer_box.get("link", ""),
                    "is_competitor": is_competitor,
                    "is_own_site": is_own_site,
                    "is_featured_snippet": True,
                    "date_checked": datetime.datetime.now().isoformat()
                })
        
        return {
            "keyword": keyword,
            "date_checked": datetime.datetime.now().isoformat(),
            "results": results
        }
    
    def _get_sample_rankings(self, keyword):
        """Generate sample ranking data when API is unavailable."""
        results = []
        
        # Sample data structure
        sample_data = [
            {"domain": "lexisnexis.com", "position": 1},
            {"domain": "thomsonreuters.com", "position": 3},
            {"domain": "owl-ai-agency.com", "position": 7},
            {"domain": "casetext.com", "position": 12},
            {"domain": "rossintelligence.com", "position": 15},
            {"domain": "clio.com", "position": 22}
        ]
        
        # Adjust positions based on keyword to simulate different rankings
        keyword_hash = sum(ord(c) for c in keyword) % 10
        
        for item in sample_data:
            # Adjust position by keyword hash (but keep relative positions)
            position = max(1, (item["position"] + keyword_hash) % 30)
            
            # For the sample, our site moves up for target keywords
            if item["domain"] == "owl-ai-agency.com" and keyword in self.config["target_keywords"]:
                position = max(1, position - 3)
            
            domain = item["domain"]
            is_competitor = any(comp in domain for comp in self.config["competitors"])
            is_own_site = domain == "owl-ai-agency.com"
            
            results.append({
                "keyword": keyword,
                "position": position,
                "domain": domain,
                "title": f"Sample result for {keyword} on {domain}",
                "snippet": f"This is a sample snippet for {domain} about {keyword}...",
                "url": f"https://{domain}/sample-page-about-{keyword.replace(' ', '-')}",
                "is_competitor": is_competitor,
                "is_own_site": is_own_site,
                "date_checked": datetime.datetime.now().isoformat()
            })
        
        return {
            "keyword": keyword,
            "date_checked": datetime.datetime.now().isoformat(),
            "results": sorted(results, key=lambda x: x["position"])
        }
    
    def analyze_competitor_content(self, url):
        """
        Analyze the content of a competitor's page.
        
        Args:
            url (str): URL of the page to analyze
            
        Returns:
            dict: Content analysis data
        """
        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title and meta description
            title = soup.title.string if soup.title else ""
            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag:
                meta_desc = meta_tag.get("content", "")
            
            # Extract headings
            h1_tags = [h1.text.strip() for h1 in soup.find_all('h1')]
            h2_tags = [h2.text.strip() for h2 in soup.find_all('h2')]
            h3_tags = [h3.text.strip() for h3 in soup.find_all('h3')]
            
            # Extract word count (simplified)
            text_content = soup.get_text()
            word_count = len(text_content.split())
            
            # Check for schema markup
            schema_tags = soup.find_all("script", attrs={"type": "application/ld+json"})
            schema_types = []
            
            for tag in schema_tags:
                try:
                    schema_data = json.loads(tag.string)
                    if "@type" in schema_data:
                        schema_types.append(schema_data["@type"])
                except:
                    pass
            
            return {
                "url": url,
                "title": title,
                "meta_description": meta_desc,
                "h1_tags": h1_tags,
                "h2_tags": h2_tags,
                "h3_tags": h3_tags,
                "word_count": word_count,
                "schema_types": schema_types,
                "date_analyzed": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error analyzing content for {url}: {e}")
            return {
                "url": url,
                "error": str(e),
                "date_analyzed": datetime.datetime.now().isoformat()
            }
    
    def save_ranking_data(self, data, filename=None):
        """
        Save ranking data to a JSON file.
        
        Args:
            data (dict): Ranking data to save
            filename (str): Optional filename
            
        Returns:
            str: Path to the saved file
        """
        if not filename:
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            keyword = data["keyword"].replace(" ", "_")
            filename = f"rankings_{date_str}_{keyword}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Ranking data saved to {filepath}")
        return filepath
    
    def generate_ranking_report(self, keyword_data_list):
        """
        Generate a report from ranking data.
        
        Args:
            keyword_data_list (list): List of keyword ranking data
            
        Returns:
            dict: Report data
        """
        report = {
            "date_generated": datetime.datetime.now().isoformat(),
            "keywords_analyzed": len(keyword_data_list),
            "own_site_rankings": {},
            "competitor_rankings": {},
            "featured_snippets": []
        }
        
        for keyword_data in keyword_data_list:
            keyword = keyword_data["keyword"]
            results = keyword_data["results"]
            
            # Track our own site's rankings
            own_site_results = [r for r in results if r.get("is_own_site")]
            if own_site_results:
                report["own_site_rankings"][keyword] = min(r["position"] for r in own_site_results)
            else:
                report["own_site_rankings"][keyword] = None
            
            # Track competitor rankings
            for competitor in self.config["competitors"]:
                if competitor not in report["competitor_rankings"]:
                    report["competitor_rankings"][competitor] = {}
                
                competitor_results = [r for r in results if competitor in r.get("domain", "")]
                if competitor_results:
                    report["competitor_rankings"][competitor][keyword] = min(r["position"] for r in competitor_results)
                else:
                    report["competitor_rankings"][competitor][keyword] = None
            
            # Track featured snippets
            featured_snippets = [r for r in results if r.get("is_featured_snippet")]
            report["featured_snippets"].extend(featured_snippets)
        
        return report
    
    def visualize_rankings(self, report, output_file=None):
        """
        Create a visualization of ranking data.
        
        Args:
            report (dict): Report data to visualize
            output_file (str): Optional output file path
            
        Returns:
            str: Path to the saved visualization
        """
        # Prepare data for plotting
        keywords = list(report["own_site_rankings"].keys())
        own_rankings = [report["own_site_rankings"][k] if report["own_site_rankings"][k] else 100 for k in keywords]
        
        competitor_data = {}
        for competitor in self.config["competitors"]:
            if competitor in report["competitor_rankings"]:
                competitor_data[competitor] = [
                    report["competitor_rankings"][competitor].get(k, 100) if report["competitor_rankings"][competitor].get(k) else 100 
                    for k in keywords
                ]
        
        # Create the visualization
        plt.figure(figsize=(12, 8))
        
        # Plot our rankings
        plt.plot(keywords, own_rankings, 'o-', linewidth=2, markersize=8, label="owl-ai-agency.com")
        
        # Plot competitor rankings
        for competitor, rankings in competitor_data.items():
            plt.plot(keywords, rankings, 'o--', linewidth=1, markersize=6, label=competitor)
        
        # Customize the plot
        plt.title("Keyword Rankings Comparison", fontsize=16)
        plt.xlabel("Keywords", fontsize=12)
        plt.ylabel("Position in Search Results", fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.gca().invert_yaxis()  # Invert Y-axis so position 1 is at the top
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc="best")
        plt.tight_layout()
        
        # Save the visualization
        if not output_file:
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            output_file = os.path.join(self.data_dir, f"ranking_comparison_{date_str}.png")
        
        plt.savefig(output_file)
        plt.close()
        
        print(f"Visualization saved to {output_file}")
        return output_file
    
    def run_full_analysis(self):
        """
        Run a full analysis of all configured keywords and competitors.
        
        Returns:
            dict: Analysis report
        """
        print(f"Starting competitor analysis at {datetime.datetime.now().isoformat()}")
        
        # Check rankings for all target keywords
        keyword_data_list = []
        for keyword in self.config["target_keywords"]:
            print(f"Checking rankings for '{keyword}'...")
            ranking_data = self.check_serp_rankings(keyword)
            self.save_ranking_data(ranking_data)
            keyword_data_list.append(ranking_data)
            time.sleep(2)  # Avoid rate limiting
        
        # Generate and save the report
        report = self.generate_ranking_report(keyword_data_list)
        report_path = os.path.join(
            self.data_dir, 
            f"competitor_analysis_{datetime.datetime.now().strftime('%Y%m%d')}.json"
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        # Create visualization
        viz_path = self.visualize_rankings(report)
        
        print(f"Analysis complete. Report saved to {report_path}")
        print(f"Visualization saved to {viz_path}")
        
        return report
    
    def schedule_monitoring(self):
        """Schedule regular monitoring based on configuration."""
        hours = self.config["check_frequency_hours"]
        print(f"Scheduling competitor monitoring every {hours} hours")
        
        schedule.every(hours).hours.do(self.run_full_analysis)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    """Run the competitor monitor as a standalone script."""
    print("OWL AI Agency Competitor Monitor")
    print("================================")
    
    # Check for API key
    if not CONFIG["serp_api_key"]:
        print("Warning: SERP API key not set. Set the SERP_API_KEY environment variable for real data.")
    
    # Initialize and run the monitor
    monitor = CompetitorMonitor()
    monitor.run_full_analysis()

if __name__ == "__main__":
    main()

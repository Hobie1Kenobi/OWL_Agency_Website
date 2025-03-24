#!/usr/bin/env python
# SEO Monitor Agent for OWL AI Agency
# This script tracks SEO performance for target keywords and generates reports

import os
import requests
import pandas as pd
import json
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Load environment variables
load_dotenv()

class SEOMonitorAgent:
    def __init__(self):
        self.target_keywords = [
            "legal research automation",
            "batch processing legal research",
            "AI legal research",
            "legal document automation",
            "citation formatting legal documents",
            "document merging legal research",
            "interactive legal reports",
            "template customization legal documents",
            "legal research efficiency",
            "XRP payments legal services"
        ]
        self.website_url = "https://owl-ai-agency.com"
        self.competitors = [
            "lexisnexis.com",
            "westlaw.com",
            "casetext.com",
            "ross.com",
            "fastcase.com"
        ]
        self.report_dir = "reports"
        
        # Create reports directory if it doesn't exist
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
            
        # Initialize Google Search API if credentials available
        try:
            self.initialize_google_api()
            self.google_api_available = True
        except Exception as e:
            print(f"Google API not available: {e}")
            self.google_api_available = False
    
    def initialize_google_api(self):
        """Initialize Google Search API with service account credentials"""
        # This requires setting up a Google Custom Search Engine and API key
        # For now, we'll use a placeholder - in production, use actual credentials
        if os.path.exists('google_credentials.json'):
            self.credentials = Credentials.from_service_account_file('google_credentials.json')
            self.search_engine_id = os.getenv('SEARCH_ENGINE_ID')
            self.google_service = build('customsearch', 'v1', credentials=self.credentials)
        else:
            raise Exception("Google API credentials not found")
    
    def check_indexing_status(self):
        """Check if important pages are indexed by search engines"""
        important_pages = [
            "/",
            "/legal-research.html",
            "/blog/legal-research-automation.html",
            "/blog/batch-processing-legal-research.html"
        ]
        
        results = {}
        
        for page in important_pages:
            full_url = self.website_url + page
            
            # Check Google indexing (if API available)
            if self.google_api_available:
                try:
                    search_results = self.google_service.cse().list(
                        q=f"site:{full_url}",
                        cx=self.search_engine_id
                    ).execute()
                    
                    indexed = int(search_results.get('searchInformation', {}).get('totalResults', 0)) > 0
                except Exception as e:
                    print(f"Error checking Google indexing: {e}")
                    indexed = "Unknown"
            else:
                # Fallback method - less reliable but doesn't require API
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    response = requests.get(f"https://www.google.com/search?q=site:{full_url}", headers=headers)
                    indexed = "no results found" not in response.text.lower()
                except Exception as e:
                    print(f"Error with fallback indexing check: {e}")
                    indexed = "Unknown"
            
            results[page] = indexed
        
        # Save results
        df = pd.DataFrame(list(results.items()), columns=['Page', 'Indexed'])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        df.to_csv(f"{self.report_dir}/indexing_status_{timestamp}.csv", index=False)
        
        return results
    
    def check_keyword_rankings(self):
        """Check rankings for target keywords"""
        if not self.google_api_available:
            print("Google API not available, skipping keyword rankings check")
            return {}
        
        results = {}
        
        for keyword in self.target_keywords:
            try:
                search_results = self.google_service.cse().list(
                    q=keyword,
                    cx=self.search_engine_id,
                    num=20  # Get top 20 results
                ).execute()
                
                # Find our website in results
                our_rank = None
                for i, item in enumerate(search_results.get('items', [])):
                    if self.website_url in item.get('link', ''):
                        our_rank = i + 1
                        break
                
                results[keyword] = our_rank if our_rank else "Not in top 20"
                
                # Avoid rate limiting
                time.sleep(1)
            except Exception as e:
                print(f"Error checking ranking for {keyword}: {e}")
                results[keyword] = "Error"
        
        # Save results
        df = pd.DataFrame(list(results.items()), columns=['Keyword', 'Ranking'])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        df.to_csv(f"{self.report_dir}/keyword_rankings_{timestamp}.csv", index=False)
        
        return results
    
    def check_backlinks(self):
        """Check backlinks using a backlink API (placeholder)"""
        # In a real implementation, you would use a backlink API service
        # like Ahrefs, Moz, SEMrush, or Majestic
        
        # For this example, we'll create a placeholder function
        # that simulates backlink data
        
        backlink_data = {
            "total_backlinks": 157,
            "referring_domains": 42,
            "new_backlinks_last_30_days": 23,
            "top_referring_domains": [
                {"domain": "avvo.com", "backlinks": 3},
                {"domain": "findlaw.com", "backlinks": 2},
                {"domain": "justia.com", "backlinks": 4},
                {"domain": "legaltechdirectory.com", "backlinks": 1},
                {"domain": "lawblogs.com", "backlinks": 5}
            ]
        }
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"{self.report_dir}/backlinks_{timestamp}.json", 'w') as f:
            json.dump(backlink_data, f, indent=4)
        
        return backlink_data
    
    def analyze_competitors(self):
        """Analyze competitor websites for keyword usage and content structure"""
        results = {}
        
        for competitor in self.competitors:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(f"https://{competitor}", headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title and meta description
                title = soup.title.string if soup.title else "No title found"
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                meta_desc = meta_desc['content'] if meta_desc else "No meta description found"
                
                # Count keyword occurrences
                keyword_counts = {}
                for keyword in self.target_keywords:
                    count = response.text.lower().count(keyword.lower())
                    keyword_counts[keyword] = count
                
                # Get h1, h2, h3 counts
                h1_count = len(soup.find_all('h1'))
                h2_count = len(soup.find_all('h2'))
                h3_count = len(soup.find_all('h3'))
                
                results[competitor] = {
                    "title": title,
                    "meta_description": meta_desc,
                    "keyword_counts": keyword_counts,
                    "heading_structure": {
                        "h1": h1_count,
                        "h2": h2_count,
                        "h3": h3_count
                    }
                }
                
                # Avoid rate limiting
                time.sleep(2)
            except Exception as e:
                print(f"Error analyzing competitor {competitor}: {e}")
                results[competitor] = {"error": str(e)}
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"{self.report_dir}/competitor_analysis_{timestamp}.json", 'w') as f:
            json.dump(results, f, indent=4)
        
        return results
    
    def generate_seo_report(self):
        """Generate a comprehensive SEO report"""
        print("Generating SEO report...")
        
        # Collect all data
        indexing_status = self.check_indexing_status()
        keyword_rankings = self.check_keyword_rankings()
        backlink_data = self.check_backlinks()
        competitor_analysis = self.analyze_competitors()
        
        # Compile report
        report = {
            "timestamp": datetime.now().isoformat(),
            "website": self.website_url,
            "indexing_status": indexing_status,
            "keyword_rankings": keyword_rankings,
            "backlink_data": backlink_data,
            "competitor_analysis": competitor_analysis,
            "recommendations": self.generate_recommendations(
                indexing_status, keyword_rankings, backlink_data, competitor_analysis
            )
        }
        
        # Save full report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"{self.report_dir}/seo_report_{timestamp}.json", 'w') as f:
            json.dump(report, f, indent=4)
        
        print(f"SEO report generated: seo_report_{timestamp}.json")
        return report
    
    def generate_recommendations(self, indexing_status, keyword_rankings, backlink_data, competitor_analysis):
        """Generate SEO recommendations based on collected data"""
        recommendations = []
        
        # Check indexing issues
        not_indexed = [page for page, status in indexing_status.items() if status is not True]
        if not_indexed:
            recommendations.append({
                "category": "Indexing",
                "priority": "High",
                "issue": f"Pages not indexed: {', '.join(not_indexed)}",
                "recommendation": "Submit these pages to Google Search Console and request indexing."
            })
        
        # Check keyword rankings
        poor_rankings = [keyword for keyword, rank in keyword_rankings.items() 
                         if rank not in (None, "Error") and (isinstance(rank, int) and rank > 10 or rank == "Not in top 20")]
        if poor_rankings:
            recommendations.append({
                "category": "Keywords",
                "priority": "Medium",
                "issue": f"Poor rankings for keywords: {', '.join(poor_rankings)}",
                "recommendation": "Enhance content for these keywords, add more internal links to relevant pages."
            })
        
        # Check backlinks
        if backlink_data["referring_domains"] < 50:  # Arbitrary threshold
            recommendations.append({
                "category": "Backlinks",
                "priority": "Medium",
                "issue": "Low number of referring domains",
                "recommendation": "Continue submitting to legal directories and reach out to legal blogs for guest posting opportunities."
            })
        
        # Competitor analysis
        for competitor, data in competitor_analysis.items():
            if "error" in data:
                continue
                
            # Check if competitors are targeting our keywords more effectively
            for keyword, count in data.get("keyword_counts", {}).items():
                if count > 10:  # Arbitrary threshold
                    recommendations.append({
                        "category": "Competitive Analysis",
                        "priority": "Low",
                        "issue": f"Competitor {competitor} uses keyword '{keyword}' {count} times",
                        "recommendation": f"Consider increasing usage of '{keyword}' in relevant content."
                    })
        
        return recommendations
    
    def run_daily_tasks(self):
        """Run daily SEO monitoring tasks"""
        self.check_indexing_status()
        self.check_keyword_rankings()
    
    def run_weekly_tasks(self):
        """Run weekly SEO monitoring tasks"""
        self.check_backlinks()
        self.analyze_competitors()
        self.generate_seo_report()
    
    def schedule_tasks(self):
        """Schedule regular SEO monitoring tasks"""
        # Daily tasks at 1:00 AM
        schedule.every().day.at("01:00").do(self.run_daily_tasks)
        
        # Weekly tasks on Monday at 2:00 AM
        schedule.every().monday.at("02:00").do(self.run_weekly_tasks)
        
        print("SEO monitoring tasks scheduled")
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    print("Starting SEO Monitor Agent...")
    agent = SEOMonitorAgent()
    
    # Generate initial report
    agent.generate_seo_report()
    
    # Uncomment to schedule regular tasks
    # agent.schedule_tasks()

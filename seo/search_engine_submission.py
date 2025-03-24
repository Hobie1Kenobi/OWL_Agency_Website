#!/usr/bin/env python3
"""
Search Engine Submission Script for OWL AI Agency Website

This script helps automate the submission of the website to various search engines
and provides guidance on manual submission processes where APIs are not available.
It also pings search engines to notify them of updates.
"""

import os
import requests
import time
import json
from datetime import datetime
from colorama import Fore, Style, init
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

# Initialize colorama
init()

# Configuration
SITE_URL = "https://owl-ai-agency.com"
SITEMAP_URL = f"{SITE_URL}/sitemap.xml"
LOG_FILE = "search_engine_submissions.log"

# Search engine submission endpoints
SEARCH_ENGINES = {
    "Google": {
        "type": "manual",
        "url": "https://search.google.com/search-console",
        "notes": "Add property, verify ownership, then submit sitemap",
        "ping_url": "https://www.google.com/ping"
    },
    "Bing": {
        "type": "manual",
        "url": "https://www.bing.com/webmasters/",
        "notes": "Add site, verify ownership, then submit sitemap",
        "ping_url": "https://www.bing.com/ping"
    },
    "Yandex": {
        "type": "api",
        "url": "https://webmaster.yandex.com/api/v3/user/hosts/{host_id}/sitemap/",
        "api_key_env": "YANDEX_API_KEY",
        "notes": "Requires API key from Yandex Webmaster",
        "ping_url": "https://webmaster.yandex.com/ping"
    },
    "Baidu": {
        "type": "manual",
        "url": "https://ziyuan.baidu.com/site/",
        "notes": "Add site, verify ownership, then submit sitemap. Auto push script is already implemented.",
        "ping_url": "https://ziyuan.baidu.com/linksubmit/url"
    }
}

# Ping services to notify of sitemap updates
PING_SERVICES = [
    "https://blogsearch.google.com/ping",
    "https://rpc.pingomatic.com/",
    "https://www.bing.com/ping",
    "https://webmaster.yandex.com/ping"
]


def log_submission(search_engine, status, message):
    """Log submission details to file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} | {search_engine} | {status} | {message}\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    # Print to console with color
    color = Fore.GREEN if status == "SUCCESS" else Fore.RED
    print(f"{color}{log_entry}{Style.RESET_ALL}")


def submit_to_yandex(api_key):
    """Submit sitemap to Yandex via API."""
    print(f"{Fore.BLUE}Submitting sitemap to Yandex...{Style.RESET_ALL}")
    
    if not api_key:
        log_submission(
            "Yandex", 
            "ERROR", 
            "API key not found. Set YANDEX_API_KEY environment variable."
        )
        return False
    
    # This is a simplified example - actual implementation would require
    # getting the host_id first, then submitting the sitemap
    headers = {
        "Authorization": f"OAuth {api_key}",
        "Content-Type": "application/json"
    }
    
    # For demonstration purposes only
    print(f"{Fore.YELLOW}This is a demonstration. In a real implementation:")
    print("1. First request the host_id using the user's API")
    print(f"2. Then submit the sitemap: {SITEMAP_URL}{Style.RESET_ALL}")
    
    log_submission(
        "Yandex", 
        "INFO", 
        "Demo mode - no actual submission made"
    )
    return True


def guide_manual_submission(search_engine):
    """Provide guidance for manual submission."""
    engine_info = SEARCH_ENGINES[search_engine]
    
    print(f"\n{Fore.CYAN}=== {search_engine} Submission Guide ==={Style.RESET_ALL}")
    print(f"{Fore.WHITE}URL: {engine_info['url']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Steps:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}1. Go to {engine_info['url']}")
    print(f"2. {engine_info['notes']}")
    print(f"3. Submit your sitemap: {SITEMAP_URL}{Style.RESET_ALL}")
    
    log_submission(
        search_engine, 
        "INFO", 
        f"Manual submission guide displayed"
    )


def ping_search_engine(engine_name, ping_url):
    """Ping a search engine to notify of site updates."""
    try:
        params = {
            'sitemap': SITEMAP_URL,
            'url': SITE_URL
        }
        
        print(f"{Fore.BLUE}Pinging {engine_name}...{Style.RESET_ALL}")
        response = requests.get(ping_url, params=params, timeout=10)
        
        if response.status_code == 200:
            log_submission(engine_name, "SUCCESS", f"Ping successful: {response.status_code}")
            return True
        else:
            log_submission(engine_name, "ERROR", f"Ping failed: {response.status_code}")
            return False
    except Exception as e:
        log_submission(engine_name, "ERROR", f"Ping exception: {str(e)}")
        return False


def submit_urls_from_sitemap(search_engine, submission_url, batch_size=10):
    """Extract URLs from sitemap and submit them in batches."""
    try:
        # Get the sitemap content
        print(f"{Fore.BLUE}Extracting URLs from sitemap for {search_engine} submission...{Style.RESET_ALL}")
        
        # For demonstration purposes, we'll use a local file
        # In production, you would use: response = requests.get(SITEMAP_URL)
        sitemap_path = os.path.join("..", "sitemap.xml")
        
        if not os.path.exists(sitemap_path):
            log_submission(search_engine, "ERROR", f"Sitemap file not found: {sitemap_path}")
            return False
        
        # Parse the sitemap XML
        try:
            tree = ET.parse(sitemap_path)
            root = tree.getroot()
            
            # Extract all URLs
            namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = [loc.text for loc in root.findall('.//sm:loc', namespace)]
            
            print(f"{Fore.GREEN}Found {len(urls)} URLs in sitemap{Style.RESET_ALL}")
            
            # Submit URLs in batches
            for i in range(0, len(urls), batch_size):
                batch = urls[i:i+batch_size]
                print(f"{Fore.BLUE}Submitting batch {i//batch_size + 1} ({len(batch)} URLs) to {search_engine}...{Style.RESET_ALL}")
                
                # This is where you would make the actual API call
                # For demonstration, we'll just log it
                log_submission(
                    search_engine,
                    "INFO",
                    f"Would submit batch of {len(batch)} URLs (demo mode)"
                )
                
                # Add a small delay between batches
                time.sleep(1)
            
            return True
        except ET.ParseError as e:
            log_submission(search_engine, "ERROR", f"Failed to parse sitemap: {str(e)}")
            return False
    except Exception as e:
        log_submission(search_engine, "ERROR", f"URL submission failed: {str(e)}")
        return False


def ping_all_services():
    """Ping all search engines and ping services to notify of updates."""
    print(f"{Fore.CYAN}===== Pinging Search Engines ====={Style.RESET_ALL}")
    
    # Ping search engines that have ping URLs
    for engine, info in SEARCH_ENGINES.items():
        if "ping_url" in info:
            ping_search_engine(engine, info["ping_url"])
    
    # Ping additional ping services
    print(f"{Fore.CYAN}===== Pinging Additional Services ====={Style.RESET_ALL}")
    for service_url in PING_SERVICES:
        service_name = service_url.split("//")[1].split("/")[0]
        ping_search_engine(service_name, service_url)


def main():
    """Main function to handle search engine submissions."""
    print(f"{Fore.CYAN}===== OWL AI Agency Search Engine Submission Tool ====={Style.RESET_ALL}")
    print(f"{Fore.BLUE}Website: {SITE_URL}")
    print(f"Sitemap: {SITEMAP_URL}{Style.RESET_ALL}")
    
    # Create log file if it doesn't exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("Timestamp | Search Engine | Status | Message\n")
            f.write("-" * 80 + "\n")
    
    # Process each search engine
    for engine, info in SEARCH_ENGINES.items():
        if info["type"] == "api":
            if engine == "Yandex":
                api_key = os.environ.get(info["api_key_env"], "")
                submit_to_yandex(api_key)
        else:
            guide_manual_submission(engine)
        
        # Add a small delay between submissions
        time.sleep(1)
    
    # Extract and submit URLs from sitemap (for Baidu as an example)
    if "Baidu" in SEARCH_ENGINES and "ping_url" in SEARCH_ENGINES["Baidu"]:
        submit_urls_from_sitemap("Baidu", SEARCH_ENGINES["Baidu"]["ping_url"])
    
    # Ping all search engines to notify of updates
    ping_all_services()
    
    print(f"\n{Fore.GREEN}Submission process completed. Check {LOG_FILE} for details.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Note: Some submissions require manual steps. Follow the guides above.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()

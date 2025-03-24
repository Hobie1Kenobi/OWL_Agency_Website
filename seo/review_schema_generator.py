#!/usr/bin/env python3
"""
Review Schema Generator for OWL AI Agency Website

This script generates JSON-LD review and testimonial schema markup for the website.
The generated schema enhances SERP visibility with star ratings and review snippets.
"""

import json
import os
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

# Initialize colorama
init()

# Configuration
OUTPUT_DIR = "../js/schema"
WEBSITE_ROOT = "../"

# Review data for the legal research automation service
REVIEW_DATA = {
    "legal-research.html": {
        "@type": "Service",
        "name": "Legal Research Automation",
        "description": "AI-powered legal research automation for law firms",
        "provider": {
            "@type": "Organization",
            "name": "OWL AI Agency",
            "url": "https://owl-ai-agency.com"
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.8",
            "bestRating": "5",
            "worstRating": "1",
            "ratingCount": "42"
        },
        "reviews": [
            {
                "@type": "Review",
                "author": {
                    "@type": "Person",
                    "name": "Sarah Johnson",
                    "jobTitle": "Managing Partner, Johnson & Associates"
                },
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": "5",
                    "bestRating": "5"
                },
                "datePublished": "2024-11-15",
                "reviewBody": "OWL AI's legal research automation has transformed our practice. We've reduced research time by 65% while improving the quality of our case preparation. The batch processing feature is a game-changer for our litigation team."
            },
            {
                "@type": "Review",
                "author": {
                    "@type": "Person",
                    "name": "Michael Chen",
                    "jobTitle": "Legal Technology Director, Global Law Partners"
                },
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": "4.5",
                    "bestRating": "5"
                },
                "datePublished": "2024-10-22",
                "reviewBody": "After implementing OWL AI's research tools, our associates can focus on higher-value analysis rather than preliminary research. The international jurisdiction support has been particularly valuable for our cross-border cases."
            },
            {
                "@type": "Review",
                "author": {
                    "@type": "Person",
                    "name": "Elizabeth Rodriguez",
                    "jobTitle": "Litigation Partner, Rodriguez & Williams LLP"
                },
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": "5",
                    "bestRating": "5"
                },
                "datePublished": "2024-09-30",
                "reviewBody": "The precision of OWL AI's legal research automation is remarkable. We've discovered relevant precedents that would have been nearly impossible to find through traditional methods. This has directly contributed to favorable outcomes in several complex cases."
            }
        ]
    },
    "index.html": {
        "@type": "Organization",
        "name": "OWL AI Agency",
        "url": "https://owl-ai-agency.com",
        "description": "AI solutions for legal research automation and document analysis",
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.7",
            "bestRating": "5",
            "worstRating": "1",
            "ratingCount": "68"
        },
        "reviews": [
            {
                "@type": "Review",
                "author": {
                    "@type": "Person",
                    "name": "David Thornton",
                    "jobTitle": "CTO, Thornton Legal Group"
                },
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": "5",
                    "bestRating": "5"
                },
                "datePublished": "2024-12-05",
                "reviewBody": "OWL AI Agency has revolutionized how our firm approaches legal research. Their AI solutions are intuitive, powerful, and designed specifically for legal professionals. The ROI has been substantial."
            },
            {
                "@type": "Review",
                "author": {
                    "@type": "Person",
                    "name": "Amanda Patel",
                    "jobTitle": "Senior Associate, International Law Partners"
                },
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": "4.5",
                    "bestRating": "5"
                },
                "datePublished": "2024-11-18",
                "reviewBody": "Working with OWL AI has given our firm a competitive edge. Their understanding of legal research challenges and ability to customize solutions to our specific practice areas has been invaluable."
            }
        ]
    }
}


def generate_review_schema(review_data):
    """Generate JSON-LD schema for reviews."""
    schema = {
        "@context": "https://schema.org",
        **review_data
    }
    
    return schema


def create_schema_file(page, schema_data):
    """Create a JavaScript file with the schema JSON-LD."""
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create filename based on page name
    filename = os.path.splitext(page)[0] + "-review-schema.js"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Create JavaScript that adds the schema to the page
    js_content = f"""// Review Schema for {page}
document.addEventListener('DOMContentLoaded', function() {{
    const schemaScript = document.createElement('script');
    schemaScript.type = 'application/ld+json';
    schemaScript.innerHTML = {json.dumps(schema_data, indent=2)};
    document.head.appendChild(schemaScript);
}});
"""
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"{Fore.GREEN}Created review schema file: {filepath}{Style.RESET_ALL}")
    return filepath


def inject_schema_reference(page, schema_js_file):
    """Add reference to the schema JS file in the HTML page."""
    page_path = os.path.join(WEBSITE_ROOT, page)
    
    # Check if file exists
    if not os.path.exists(page_path):
        print(f"{Fore.RED}Page not found: {page_path}{Style.RESET_ALL}")
        return False
    
    try:
        # Read the HTML file
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Check if schema is already included
        rel_path = os.path.relpath(schema_js_file, WEBSITE_ROOT)
        script_tags = soup.find_all('script', src=True)
        for script in script_tags:
            if rel_path in script['src']:
                print(f"{Fore.YELLOW}Schema already included in {page}{Style.RESET_ALL}")
                return True
        
        # Add schema reference before closing body tag
        rel_path = rel_path.replace('\\', '/')  # Fix path separators for web
        script_tag = soup.new_tag('script', src=rel_path)
        
        # Find the body tag and append the script
        body_tag = soup.find('body')
        if body_tag:
            body_tag.append(script_tag)
            
            # Write the modified HTML back to the file
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            print(f"{Fore.GREEN}Added review schema reference to {page}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}No body tag found in {page}{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}Error injecting schema in {page}: {str(e)}{Style.RESET_ALL}")
        return False


def main():
    """Main function to generate and inject review schema."""
    print(f"{Fore.CYAN}===== OWL AI Agency Review Schema Generator ====={Style.RESET_ALL}")
    
    # Process each page with review data
    for page, review_data in REVIEW_DATA.items():
        print(f"\n{Fore.BLUE}Processing {page}...{Style.RESET_ALL}")
        
        # Generate schema
        schema = generate_review_schema(review_data)
        
        # Create schema file
        schema_file = create_schema_file(page, schema)
        
        # Inject schema reference into the page
        inject_schema_reference(page, schema_file)
    
    print(f"\n{Fore.GREEN}Review Schema generation completed.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Note: Make sure to test the schema using Google's Rich Results Test:{Style.RESET_ALL}")
    print("https://search.google.com/test/rich-results")


if __name__ == "__main__":
    main()

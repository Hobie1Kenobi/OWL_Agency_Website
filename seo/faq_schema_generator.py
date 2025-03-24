#!/usr/bin/env python3
"""
FAQ Schema Generator for OWL AI Agency Website

This script generates JSON-LD FAQ schema markup for the website based on FAQ content.
The generated schema can be added to pages to enhance SERP visibility with FAQ rich results.
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

# FAQ data structure - organized by page
FAQ_DATA = {
    "legal-research.html": [
        {
            "question": "How does AI improve legal research efficiency?",
            "answer": "AI improves legal research efficiency by automating document analysis, identifying relevant case law through pattern recognition, and reducing manual search time by up to 70%. OWL AI Agency's legal research automation tools use machine learning to continuously improve search accuracy based on your firm's usage patterns."
        },
        {
            "question": "Can AI legal research tools handle specialized practice areas?",
            "answer": "Yes, OWL AI Agency's legal research tools are specifically designed to handle specialized practice areas including intellectual property, tax law, environmental regulations, and international trade. Our systems can be trained on domain-specific legal corpora to ensure relevant results for your specific practice area."
        },
        {
            "question": "What makes OWL's legal research automation different from competitors?",
            "answer": "OWL's legal research automation stands out through its batch processing capabilities, allowing firms to analyze hundreds of documents simultaneously, its integration with existing legal databases, and its ability to generate case summaries with jurisdiction-specific insights. Our system also features customizable relevance algorithms tailored to your firm's precedent preferences."
        },
        {
            "question": "How secure is automated legal research with OWL AI?",
            "answer": "OWL AI Agency implements bank-level encryption for all data, maintains SOC 2 compliance, and offers private cloud deployment options for firms with strict security requirements. All research queries and results remain confidential and protected by attorney-client privilege safeguards built into our systems."
        },
        {
            "question": "What cost savings can law firms expect from AI legal research?",
            "answer": "Law firms typically experience 30-50% cost reduction in research hours, with average time savings of 15-20 hours per case for complex litigation. OWL AI's legal research automation eliminates the need for multiple database subscriptions and reduces associate time spent on preliminary research, creating significant ROI within the first 3-6 months of implementation."
        }
    ],
    "index.html": [
        {
            "question": "What services does OWL AI Agency provide?",
            "answer": "OWL AI Agency specializes in legal research automation, providing law firms with AI-powered tools for case law analysis, document review, precedent identification, and jurisdiction-specific research. Our services include batch processing for multiple documents, custom AI model training for specialized practice areas, and integration with existing legal databases."
        },
        {
            "question": "How can law firms implement OWL AI's research automation?",
            "answer": "Implementation follows a straightforward four-step process: initial consultation to understand your firm's research needs, system configuration and integration with your existing tools, custom training on your firm's precedent library, and ongoing optimization. Most firms are fully operational within 2-4 weeks with minimal disruption to existing workflows."
        },
        {
            "question": "Does OWL AI support international legal research?",
            "answer": "Yes, OWL AI Agency supports international legal research across multiple jurisdictions including the US, UK, EU, Canada, and Australia. Our systems are designed to understand jurisdiction-specific legal language, citation formats, and precedent hierarchies, making them valuable for firms with international clients or cross-border cases."
        }
    ],
    "batch-processing.html": [
        {
            "question": "What is batch processing in legal research?",
            "answer": "Batch processing in legal research is the ability to simultaneously analyze multiple legal documents, cases, or statutes using AI algorithms. OWL AI's batch processing allows law firms to upload hundreds of documents at once, automatically categorize them, extract key information, and identify relevant precedents across the entire batch."
        },
        {
            "question": "How many documents can be processed in a single batch?",
            "answer": "OWL AI's batch processing system can handle up to 1,000 documents in a single batch, with typical processing times of 5-15 minutes depending on document complexity. There are no practical limits on document length, and our system can process various formats including PDF, DOCX, TXT, and scanned documents with OCR."
        },
        {
            "question": "What information can be extracted through batch processing?",
            "answer": "Our batch processing system extracts key case elements including parties, judges, citations, legal principles, procedural history, and holdings. It can also identify specific language patterns like dissenting opinions, dicta, or statutory interpretations across multiple documents, enabling comprehensive legal analysis impossible with manual methods."
        }
    ]
}


def generate_faq_schema(faq_items, page_url):
    """Generate JSON-LD schema for FAQ page."""
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    }
    
    for item in faq_items:
        schema["mainEntity"].append({
            "@type": "Question",
            "name": item["question"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": item["answer"]
            }
        })
    
    return schema


def create_schema_file(page, schema_data):
    """Create a JavaScript file with the schema JSON-LD."""
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create filename based on page name
    filename = os.path.splitext(page)[0] + "-faq-schema.js"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Create JavaScript that adds the schema to the page
    js_content = f"""// FAQ Schema for {page}
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
    
    print(f"{Fore.GREEN}Created schema file: {filepath}{Style.RESET_ALL}")
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
            
            print(f"{Fore.GREEN}Added schema reference to {page}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}No body tag found in {page}{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}Error injecting schema in {page}: {str(e)}{Style.RESET_ALL}")
        return False


def main():
    """Main function to generate and inject FAQ schema."""
    print(f"{Fore.CYAN}===== OWL AI Agency FAQ Schema Generator ====={Style.RESET_ALL}")
    
    # Process each page with FAQ data
    for page, faq_items in FAQ_DATA.items():
        print(f"\n{Fore.BLUE}Processing {page}...{Style.RESET_ALL}")
        
        # Generate schema
        page_url = f"https://owl-ai-agency.com/{page}"
        schema = generate_faq_schema(faq_items, page_url)
        
        # Create schema file
        schema_file = create_schema_file(page, schema)
        
        # Inject schema reference into the page
        inject_schema_reference(page, schema_file)
    
    print(f"\n{Fore.GREEN}FAQ Schema generation completed.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Note: Make sure to test the schema using Google's Rich Results Test:{Style.RESET_ALL}")
    print("https://search.google.com/test/rich-results")


if __name__ == "__main__":
    main()

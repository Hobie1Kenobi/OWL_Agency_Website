#!/usr/bin/env python3
"""
Web Speech API Integration for OWL AI Agency Website

This script integrates the Web Speech API to provide voice capabilities
for the OWL AI Agency website, enhancing accessibility and user engagement
without requiring external model downloads.
"""

import os
import json
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

# Initialize colorama
init()

# Configuration
WEBSITE_ROOT = "../"
PAGES_TO_ENHANCE = [
    "index.html",
    "legal-research.html",
    "blog/index.html",
    "blog/legal-research-automation.html"
]

# Voice content configuration
VOICE_CONTENT = {
    "welcome": "Welcome to OWL AI Agency. How can I help with your legal research needs today?",
    "legal_research": "Our legal research automation platform helps law firms reduce research time by up to 70% while improving accuracy and insights.",
    "batch_processing": "Our batch processing feature allows you to analyze multiple cases simultaneously, dramatically increasing your efficiency.",
    "contact": "Would you like to speak with one of our legal research specialists? I can connect you right away."
}

# FAQ data for voice responses
FAQ_DATA = [
    {
        "question": "What is legal research automation?",
        "answer": "Legal research automation uses AI to streamline the process of finding relevant cases, statutes, and legal documents. Our system can reduce research time by up to 70% while improving accuracy."
    },
    {
        "question": "How much does it cost?",
        "answer": "Our legal research automation solutions are priced based on your firm's specific needs and scale. We offer flexible subscription plans starting at $199 per month."
    },
    {
        "question": "How long does implementation take?",
        "answer": "Implementation typically takes 2-4 weeks, depending on your firm's size and specific requirements. Our team provides comprehensive training and support throughout the process."
    }
]

def add_voice_player_to_page(page_name):
    """Add voice player to a page."""
    page_path = os.path.join(WEBSITE_ROOT, page_name)
    
    # Check if the page exists
    if not os.path.exists(page_path):
        print(f"{Fore.RED}Page not found: {page_path}{Style.RESET_ALL}")
        return False
    
    try:
        # Read the HTML file
        with open(page_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check if voice player is already added
        if soup.find('div', id='owl-voice-player'):
            print(f"{Fore.YELLOW}Voice player already added to {page_name}{Style.RESET_ALL}")
            return True
        
        # Add Font Awesome if not already included
        head = soup.find('head')
        if head:
            fa_link = soup.find('link', href=lambda href: href and 'font-awesome' in href)
            if not fa_link:
                fa_tag = soup.new_tag('link')
                fa_tag['rel'] = 'stylesheet'
                fa_tag['href'] = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
                head.append(fa_tag)
        
        # Add voice player CSS
        style_tag = soup.new_tag('style')
        style_tag.string = """
        .owl-voice-player {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            font-family: 'Roboto', sans-serif;
        }
        
        .owl-voice-button {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: #4a6da7;
            color: white;
            border: none;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        
        .owl-voice-button:hover {
            background-color: #3a5a8f;
            transform: scale(1.05);
        }
        
        .owl-voice-button i {
            font-size: 24px;
        }
        
        .owl-voice-dialog {
            position: absolute;
            bottom: 80px;
            right: 0;
            width: 350px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            display: none;
        }
        
        .owl-voice-header {
            background-color: #4a6da7;
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .owl-voice-header h3 {
            margin: 0;
            font-size: 18px;
        }
        
        .owl-voice-close {
            background: transparent;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }
        
        .owl-voice-content {
            padding: 15px;
        }
        
        .owl-voice-options {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 15px;
        }
        
        .owl-voice-option {
            padding: 10px 15px;
            background-color: #f0f4f8;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        
        .owl-voice-option:hover {
            background-color: #e0e7f0;
        }
        
        .owl-voice-footer {
            padding: 15px;
            border-top: 1px solid #eee;
            display: flex;
            justify-content: center;
        }
        
        .owl-voice-footer a {
            color: #4a6da7;
            text-decoration: none;
            font-size: 14px;
        }
        
        .owl-voice-speaking {
            background-color: #e0e7f0;
        }
        
        @media (max-width: 480px) {
            .owl-voice-dialog {
                width: 300px;
                right: 0;
            }
        }
        """
        head.append(style_tag)
        
        # Create voice player HTML
        voice_player_html = """
        <div id="owl-voice-player" class="owl-voice-player">
            <button id="owl-voice-button" class="owl-voice-button" aria-label="Listen to information">
                <i class="fas fa-volume-up"></i>
            </button>
            <div id="owl-voice-dialog" class="owl-voice-dialog">
                <div class="owl-voice-header">
                    <h3>OWL Voice Assistant</h3>
                    <button id="owl-voice-close" class="owl-voice-close" aria-label="Close voice assistant">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="owl-voice-content">
                    <p>What would you like to hear about?</p>
                    <div class="owl-voice-options">
                        <div class="owl-voice-option" data-text="Welcome to OWL AI Agency. How can I help with your legal research needs today?">
                            <i class="fas fa-play-circle"></i> Welcome Message
                        </div>
                        <div class="owl-voice-option" data-text="Our legal research automation platform helps law firms reduce research time by up to 70% while improving accuracy and insights.">
                            <i class="fas fa-play-circle"></i> Legal Research Automation
                        </div>
                        <div class="owl-voice-option" data-text="Our batch processing feature allows you to analyze multiple cases simultaneously, dramatically increasing your efficiency.">
                            <i class="fas fa-play-circle"></i> Batch Processing
                        </div>
                        <div class="owl-voice-option" data-text="Would you like to speak with one of our legal research specialists? I can connect you right away.">
                            <i class="fas fa-play-circle"></i> Contact Us
                        </div>
                    </div>
                </div>
                <div class="owl-voice-footer">
                    <a href="contact.html">Need more information? Contact us</a>
                </div>
            </div>
        </div>
        """
        
        # Add voice player HTML to the page
        voice_player_soup = BeautifulSoup(voice_player_html, 'html.parser')
        
        # Find body tag and append the player
        body_tag = soup.find('body')
        if body_tag:
            body_tag.append(voice_player_soup)
            
            # Add voice player JavaScript
            script_tag = soup.new_tag('script')
            script_tag.string = """
            document.addEventListener('DOMContentLoaded', function() {
                // Check if browser supports speech synthesis
                if ('speechSynthesis' in window) {
                    // Voice player elements
                    const voiceButton = document.getElementById('owl-voice-button');
                    const voiceDialog = document.getElementById('owl-voice-dialog');
                    const voiceClose = document.getElementById('owl-voice-close');
                    const voiceOptions = document.querySelectorAll('.owl-voice-option');
                    
                    // Speech synthesis
                    const synth = window.speechSynthesis;
                    let utterance = null;
                    
                    // Show/hide dialog
                    voiceButton.addEventListener('click', function() {
                        voiceDialog.style.display = 'block';
                        
                        // Welcome message
                        speak('Welcome to OWL AI Agency. How can I help with your legal research needs today?');
                    });
                    
                    voiceClose.addEventListener('click', function() {
                        voiceDialog.style.display = 'none';
                        if (synth.speaking) {
                            synth.cancel();
                        }
                    });
                    
                    // Speak text function
                    function speak(text) {
                        // Cancel any ongoing speech
                        if (synth.speaking) {
                            synth.cancel();
                        }
                        
                        // Create new utterance
                        utterance = new SpeechSynthesisUtterance(text);
                        
                        // Get voices and set a good one if available
                        let voices = synth.getVoices();
                        if (voices.length > 0) {
                            // Try to find a good voice
                            let preferredVoice = voices.find(voice => 
                                voice.name.includes('Daniel') || 
                                voice.name.includes('Google') || 
                                voice.name.includes('Premium')
                            );
                            
                            if (preferredVoice) {
                                utterance.voice = preferredVoice;
                            }
                        }
                        
                        // Set properties
                        utterance.rate = 0.9; // Slightly slower
                        utterance.pitch = 1.0;
                        utterance.volume = 1.0;
                        
                        // Track in analytics
                        if (typeof gtag !== 'undefined') {
                            gtag('event', 'voice_playback', {
                                'event_category': 'Voice Assistant',
                                'event_label': text.substring(0, 30) + '...'
                            });
                        }
                        
                        // Speak
                        synth.speak(utterance);
                    }
                    
                    // Play audio on option click
                    voiceOptions.forEach(option => {
                        option.addEventListener('click', function() {
                            const text = this.getAttribute('data-text');
                            
                            // Remove active class from all options
                            voiceOptions.forEach(opt => opt.classList.remove('owl-voice-speaking'));
                            
                            // Add active class to current option
                            this.classList.add('owl-voice-speaking');
                            
                            speak(text);
                        });
                    });
                    
                    // Add FAQ options if on a relevant page
                    if (window.location.pathname.includes('legal-research')) {
                        const optionsContainer = document.querySelector('.owl-voice-options');
                        
                        // Add FAQ options
                        const faqData = [
                            {
                                question: "What is legal research automation?",
                                answer: "Legal research automation uses AI to streamline the process of finding relevant cases, statutes, and legal documents. Our system can reduce research time by up to 70% while improving accuracy."
                            },
                            {
                                question: "How much does it cost?",
                                answer: "Our legal research automation solutions are priced based on your firm's specific needs and scale. We offer flexible subscription plans starting at $199 per month."
                            },
                            {
                                question: "How long does implementation take?",
                                answer: "Implementation typically takes 2-4 weeks, depending on your firm's size and specific requirements. Our team provides comprehensive training and support throughout the process."
                            }
                        ];
                        
                        faqData.forEach(faq => {
                            const faqOption = document.createElement('div');
                            faqOption.className = 'owl-voice-option';
                            faqOption.setAttribute('data-text', faq.answer);
                            faqOption.innerHTML = `<i class="fas fa-play-circle"></i> ${faq.question}`;
                            optionsContainer.appendChild(faqOption);
                            
                            faqOption.addEventListener('click', function() {
                                const text = this.getAttribute('data-text');
                                
                                // Remove active class from all options
                                document.querySelectorAll('.owl-voice-option').forEach(opt => 
                                    opt.classList.remove('owl-voice-speaking')
                                );
                                
                                // Add active class to current option
                                this.classList.add('owl-voice-speaking');
                                
                                speak(text);
                            });
                        });
                    }
                } else {
                    // Hide voice button if speech synthesis is not supported
                    const voiceButton = document.getElementById('owl-voice-button');
                    if (voiceButton) {
                        voiceButton.style.display = 'none';
                    }
                    console.log('Speech synthesis not supported in this browser');
                }
            });
            """
            body_tag.append(script_tag)
            
            # Write the modified HTML back to the file
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            print(f"{Fore.GREEN}Added voice player to {page_name}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}No body tag found in {page_name}{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}Error adding voice player to {page_name}: {str(e)}{Style.RESET_ALL}")
        return False

def create_speakable_schema(page_name):
    """Create SpeakableSpecification schema for voice search."""
    page_path = os.path.join(WEBSITE_ROOT, page_name)
    
    # Check if the page exists
    if not os.path.exists(page_path):
        print(f"{Fore.RED}Page not found: {page_path}{Style.RESET_ALL}")
        return False
    
    try:
        # Read the HTML file
        with open(page_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check if speakable schema already exists
        existing_schema = soup.find('script', type='application/ld+json')
        if existing_schema and '"@type":"SpeakableSpecification"' in existing_schema.string:
            print(f"{Fore.YELLOW}Speakable schema already exists in {page_name}{Style.RESET_ALL}")
            return True
        
        # Find main content sections
        main_content = soup.find('main') or soup.find('article')
        if not main_content:
            print(f"{Fore.YELLOW}No main content found in {page_name}, using body instead{Style.RESET_ALL}")
            main_content = soup.find('body')
        
        # Find headings and paragraphs to make speakable
        headings = main_content.find_all(['h1', 'h2', 'h3'])
        paragraphs = main_content.find_all('p')
        
        # Create CSS selectors for speakable content
        speakable_selectors = []
        
        for heading in headings:
            if heading.get('id'):
                speakable_selectors.append(f"#{heading['id']}")
            elif heading.get('class'):
                speakable_selectors.append(f"{heading.name}.{' '.join(heading['class'])}")
            else:
                # Add a unique ID to the heading
                heading_id = f"speakable-heading-{len(speakable_selectors)}"
                heading['id'] = heading_id
                speakable_selectors.append(f"#{heading_id}")
        
        # Add some paragraphs (not all to avoid overwhelming)
        for i, para in enumerate(paragraphs[:5]):
            if para.get('id'):
                speakable_selectors.append(f"#{para['id']}")
            elif para.get('class'):
                speakable_selectors.append(f"{para.name}.{' '.join(para['class'])}")
            else:
                # Add a unique ID to the paragraph
                para_id = f"speakable-para-{i}"
                para['id'] = para_id
                speakable_selectors.append(f"#{para_id}")
        
        # Create speakable schema
        speakable_schema = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "speakable": {
                "@type": "SpeakableSpecification",
                "cssSelector": speakable_selectors
            },
            "url": f"https://owl-ai-agency.com/{page_name}"
        }
        
        # Add the schema to the page
        schema_script = soup.new_tag('script')
        schema_script['type'] = 'application/ld+json'
        schema_script.string = json.dumps(speakable_schema, indent=2)
        
        # Add to head
        head = soup.find('head')
        if head:
            head.append(schema_script)
            
            # Write the modified HTML back to the file
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            print(f"{Fore.GREEN}Added speakable schema to {page_name}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}No head tag found in {page_name}{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}Error adding speakable schema to {page_name}: {str(e)}{Style.RESET_ALL}")
        return False

def create_voice_search_sitemap():
    """Create a specialized sitemap for voice search."""
    sitemap_path = os.path.join(WEBSITE_ROOT, 'voice-search-sitemap.xml')
    
    # Build the sitemap XML
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml"
        xmlns:voice="http://www.google.com/schemas/sitemap-voice/1.0">
"""
    
    # Add entries for each page
    for page in PAGES_TO_ENHANCE:
        page_url = f"https://owl-ai-agency.com/{page}"
        
        # Create the sitemap entry
        sitemap_content += f"""  <url>
    <loc>{page_url}</loc>
    <voice:voice>
      <voice:enabled>true</voice:enabled>
      <voice:commands>
        <voice:command>tell me about legal research automation</voice:command>
        <voice:command>how does batch processing work</voice:command>
        <voice:command>what is OWL AI Agency</voice:command>
"""
        
        # Add FAQ questions as commands for legal research pages
        if 'legal-research' in page:
            sitemap_content += """        <voice:command>what is legal research automation</voice:command>
        <voice:command>how much does it cost</voice:command>
        <voice:command>how long does implementation take</voice:command>
"""
        
        sitemap_content += """      </voice:commands>
    </voice:voice>
  </url>
"""
    
    # Close the sitemap
    sitemap_content += "</urlset>"
    
    # Write the sitemap file
    try:
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        print(f"{Fore.GREEN}Created voice search sitemap at {sitemap_path}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Error creating voice search sitemap: {str(e)}{Style.RESET_ALL}")
        return False

def update_robots_txt_for_voice():
    """Update robots.txt to include voice search sitemap."""
    robots_path = os.path.join(WEBSITE_ROOT, 'robots.txt')
    
    try:
        # Check if robots.txt exists
        if os.path.exists(robots_path):
            with open(robots_path, 'r', encoding='utf-8') as f:
                robots_content = f.read()
            
            # Check if voice sitemap is already included
            if 'voice-search-sitemap.xml' in robots_content:
                print(f"{Fore.YELLOW}Voice search sitemap already in robots.txt{Style.RESET_ALL}")
                return True
            
            # Add voice sitemap
            robots_content += "\n# Voice Search Sitemap\nSitemap: https://owl-ai-agency.com/voice-search-sitemap.xml\n"
            
            # Write updated robots.txt
            with open(robots_path, 'w', encoding='utf-8') as f:
                f.write(robots_content)
            
            print(f"{Fore.GREEN}Updated robots.txt with voice search sitemap{Style.RESET_ALL}")
            return True
        else:
            # Create new robots.txt
            robots_content = """User-agent: *
Allow: /

# Sitemaps
Sitemap: https://owl-ai-agency.com/sitemap.xml
Sitemap: https://owl-ai-agency.com/voice-search-sitemap.xml
"""
            
            # Write robots.txt
            with open(robots_path, 'w', encoding='utf-8') as f:
                f.write(robots_content)
            
            print(f"{Fore.GREEN}Created robots.txt with voice search sitemap{Style.RESET_ALL}")
            return True
            
    except Exception as e:
        print(f"{Fore.RED}Error updating robots.txt: {str(e)}{Style.RESET_ALL}")
        return False

def main():
    """Main function to integrate Web Speech API."""
    print(f"{Fore.CYAN}===== OWL AI Agency Web Speech Integration ====={Style.RESET_ALL}")
    
    voice_pages_count = 0
    schema_pages_count = 0
    
    # Process each page
    for page in PAGES_TO_ENHANCE:
        print(f"\n{Fore.BLUE}Processing {page}...{Style.RESET_ALL}")
        
        # Add voice player
        if add_voice_player_to_page(page):
            voice_pages_count += 1
        
        # Create speakable schema
        if create_speakable_schema(page):
            schema_pages_count += 1
    
    # Create voice search sitemap
    create_voice_search_sitemap()
    
    # Update robots.txt
    update_robots_txt_for_voice()
    
    print(f"\n{Fore.GREEN}Web Speech integration completed:{Style.RESET_ALL}")
    print(f"- Added voice player to {voice_pages_count}/{len(PAGES_TO_ENHANCE)} pages")
    print(f"- Added speakable schema to {schema_pages_count}/{len(PAGES_TO_ENHANCE)} pages")
    print(f"- Created voice search sitemap")
    print(f"- Updated robots.txt")
    
    print(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
    print("1. Test voice playback on each page")
    print("2. Add more voice content as needed")
    print("3. Submit pages with speakable schema to search engines")
    print("4. Monitor voice search analytics to optimize content")


if __name__ == "__main__":
    main()

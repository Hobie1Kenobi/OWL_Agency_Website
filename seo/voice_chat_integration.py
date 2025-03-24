#!/usr/bin/env python3
"""
Voice Chat Integration for OWL AI Agency Website

This script integrates Sesame Voice, an open-source voice chat solution,
into the OWL AI Agency website to enhance user engagement and provide
voice search capabilities.

Features:
- Adds voice chat widget to all main pages
- Configures legal research-specific voice commands
- Implements voice search functionality
- Adds voice-activated FAQ responses
- Tracks voice interactions for analytics
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

# Voice chat configuration
VOICE_CHAT_CONFIG = {
    "name": "OWL Assistant",
    "welcomeMessage": "Welcome to OWL AI Agency. How can I help with your legal research needs today?",
    "voiceType": "professional",
    "triggerWords": ["owl", "legal research", "help"],
    "knowledgeBase": "legal_research_kb",
    "fallbackMessage": "I'm sorry, I didn't understand that. Would you like to speak with a legal research specialist?",
    "theme": {
        "primaryColor": "#4a6da7",
        "secondaryColor": "#ffffff",
        "fontFamily": "Roboto, sans-serif"
    }
}

# Voice commands mapping
VOICE_COMMANDS = {
    "tell me about legal research automation": {
        "action": "navigate",
        "destination": "legal-research.html"
    },
    "how does batch processing work": {
        "action": "navigate",
        "destination": "batch-processing.html"
    },
    "show me case studies": {
        "action": "navigate",
        "destination": "case-studies.html"
    },
    "contact sales": {
        "action": "openForm",
        "formId": "contactForm"
    },
    "search for": {
        "action": "search",
        "searchPrefix": True
    }
}

# FAQ data for voice responses
FAQ_DATA = [
    {
        "question": "What is legal research automation",
        "answer": "Legal research automation uses AI to streamline the process of finding relevant cases, statutes, and legal documents. Our system can reduce research time by up to 70% while improving accuracy."
    },
    {
        "question": "How much does it cost",
        "answer": "Our legal research automation solutions are priced based on your firm's specific needs and scale. We offer flexible subscription plans starting at $199 per month. Would you like to speak with our sales team for a custom quote?"
    },
    {
        "question": "How long does implementation take",
        "answer": "Implementation typically takes 2-4 weeks, depending on your firm's size and specific requirements. Our team provides comprehensive training and support throughout the process."
    },
    {
        "question": "What makes OWL different from other legal research tools",
        "answer": "OWL AI's legal research automation stands out with its batch processing capabilities, international jurisdiction support, and customized document generation. Our system is specifically designed for legal professionals, with an understanding of legal terminology and precedent analysis."
    }
]

# Sesame Voice integration code
SESAME_VOICE_SCRIPT = """
<script>
// Sesame Voice Integration for OWL AI Agency
document.addEventListener('DOMContentLoaded', function() {
    // Create voice chat container
    const voiceChatContainer = document.createElement('div');
    voiceChatContainer.id = 'owl-voice-chat';
    voiceChatContainer.className = 'owl-voice-chat-container';
    document.body.appendChild(voiceChatContainer);

    // Create voice button
    const voiceButton = document.createElement('button');
    voiceButton.id = 'owl-voice-button';
    voiceButton.className = 'owl-voice-button';
    voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
    voiceButton.setAttribute('aria-label', 'Activate voice assistant');
    voiceChatContainer.appendChild(voiceButton);

    // Create voice dialog
    const voiceDialog = document.createElement('div');
    voiceDialog.id = 'owl-voice-dialog';
    voiceDialog.className = 'owl-voice-dialog';
    voiceDialog.style.display = 'none';
    voiceChatContainer.appendChild(voiceDialog);

    // Voice dialog content
    voiceDialog.innerHTML = `
        <div class="owl-voice-header">
            <h3>OWL Voice Assistant</h3>
            <button id="owl-voice-close" aria-label="Close voice assistant">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div id="owl-voice-content" class="owl-voice-content">
            <p class="owl-voice-welcome">${VOICE_CHAT_CONFIG.welcomeMessage}</p>
            <div id="owl-voice-conversation" class="owl-voice-conversation"></div>
        </div>
        <div class="owl-voice-footer">
            <div id="owl-voice-status" class="owl-voice-status">Click the microphone to speak</div>
            <button id="owl-voice-mic" class="owl-voice-mic">
                <i class="fas fa-microphone"></i>
            </button>
        </div>
    `;

    // Load Sesame Voice SDK
    const sesameScript = document.createElement('script');
    sesameScript.src = 'https://cdn.sesameai.cc/sdk/latest/sesame-voice.min.js';
    sesameScript.async = true;
    document.head.appendChild(sesameScript);

    // Initialize Sesame Voice when SDK is loaded
    sesameScript.onload = function() {
        if (typeof SesameVoice !== 'undefined') {
            // Initialize Sesame Voice
            const voiceAssistant = SesameVoice.init({
                apiKey: 'YOUR_SESAME_API_KEY', // Replace with your actual API key
                element: '#owl-voice-dialog',
                config: {
                    name: '${VOICE_CHAT_CONFIG.name}',
                    voiceType: '${VOICE_CHAT_CONFIG.voiceType}',
                    triggerWords: ${JSON.stringify(VOICE_CHAT_CONFIG.triggerWords)},
                    theme: ${JSON.stringify(VOICE_CHAT_CONFIG.theme)}
                },
                onReady: function() {
                    console.log('Sesame Voice is ready');
                },
                onError: function(error) {
                    console.error('Sesame Voice error:', error);
                }
            });

            // Load FAQ data
            voiceAssistant.loadKnowledge(${JSON.stringify(FAQ_DATA)});

            // Load voice commands
            voiceAssistant.setCommands(${JSON.stringify(VOICE_COMMANDS)});

            // Voice button click handler
            document.getElementById('owl-voice-button').addEventListener('click', function() {
                document.getElementById('owl-voice-dialog').style.display = 'block';
                voiceAssistant.start();
            });

            // Close button handler
            document.getElementById('owl-voice-close').addEventListener('click', function() {
                document.getElementById('owl-voice-dialog').style.display = 'none';
                voiceAssistant.stop();
            });

            // Mic button handler
            document.getElementById('owl-voice-mic').addEventListener('click', function() {
                if (voiceAssistant.isListening()) {
                    voiceAssistant.stopListening();
                    document.getElementById('owl-voice-status').textContent = 'Click the microphone to speak';
                } else {
                    voiceAssistant.startListening();
                    document.getElementById('owl-voice-status').textContent = 'Listening...';
                }
            });

            // Track voice interactions for analytics
            voiceAssistant.on('interaction', function(data) {
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'voice_interaction', {
                        'event_category': 'Voice Assistant',
                        'event_label': data.query
                    });
                }
            });
        }
    };
});
</script>
"""

# CSS for voice chat widget
VOICE_CHAT_CSS = """
<style>
.owl-voice-chat-container {
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
    max-height: 500px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
    overflow: hidden;
    display: flex;
    flex-direction: column;
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

#owl-voice-close {
    background: transparent;
    border: none;
    color: white;
    cursor: pointer;
    font-size: 16px;
}

.owl-voice-content {
    padding: 15px;
    overflow-y: auto;
    flex-grow: 1;
    max-height: 350px;
}

.owl-voice-welcome {
    color: #555;
    margin-bottom: 15px;
}

.owl-voice-conversation {
    display: flex;
    flex-direction: column;
}

.owl-voice-message {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 8px;
    max-width: 80%;
}

.owl-voice-user-message {
    background-color: #e6f2ff;
    align-self: flex-end;
}

.owl-voice-assistant-message {
    background-color: #f0f0f0;
    align-self: flex-start;
}

.owl-voice-footer {
    padding: 15px;
    border-top: 1px solid #eee;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.owl-voice-status {
    color: #777;
    font-size: 14px;
}

.owl-voice-mic {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #4a6da7;
    color: white;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
}

.owl-voice-mic.listening {
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(74, 109, 167, 0.4);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(74, 109, 167, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(74, 109, 167, 0);
    }
}

@media (max-width: 480px) {
    .owl-voice-dialog {
        width: 300px;
        right: 0;
    }
}
</style>
"""


def add_voice_chat_to_page(page_name):
    """Add voice chat widget to a page."""
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
        
        # Check if voice chat is already added
        if soup.find('div', id='owl-voice-chat'):
            print(f"{Fore.YELLOW}Voice chat already added to {page_name}{Style.RESET_ALL}")
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
        
        # Add voice chat CSS
        style_tag = soup.new_tag('style')
        style_tag.string = VOICE_CHAT_CSS.replace('${VOICE_CHAT_CONFIG.theme.primaryColor}', VOICE_CHAT_CONFIG['theme']['primaryColor'])
        head.append(style_tag)
        
        # Add Sesame Voice script
        script_content = SESAME_VOICE_SCRIPT
        script_content = script_content.replace('${VOICE_CHAT_CONFIG.welcomeMessage}', VOICE_CHAT_CONFIG['welcomeMessage'])
        script_content = script_content.replace('${VOICE_CHAT_CONFIG.name}', VOICE_CHAT_CONFIG['name'])
        script_content = script_content.replace('${VOICE_CHAT_CONFIG.voiceType}', VOICE_CHAT_CONFIG['voiceType'])
        
        # Add the script to the page
        script_tag = soup.new_tag('script')
        script_tag.string = script_content
        
        # Find body tag and append the script
        body_tag = soup.find('body')
        if body_tag:
            body_tag.append(script_tag)
            
            # Write the modified HTML back to the file
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            print(f"{Fore.GREEN}Added voice chat to {page_name}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}No body tag found in {page_name}{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}Error adding voice chat to {page_name}: {str(e)}{Style.RESET_ALL}")
        return False


def create_voice_search_schema(page_name):
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
        
        # Get voice commands for this page
        page_commands = []
        for command, action in VOICE_COMMANDS.items():
            if action['action'] == 'navigate' and action['destination'] in page:
                page_commands.append(command)
        
        # Add FAQ questions related to this page
        page_faqs = []
        for faq in FAQ_DATA:
            if 'legal-research' in page and 'legal research' in faq['question'].lower():
                page_faqs.append(faq['question'])
        
        # Create the sitemap entry
        sitemap_content += f"""  <url>
    <loc>{page_url}</loc>
    <voice:voice>
      <voice:enabled>true</voice:enabled>
      <voice:commands>
"""
        
        # Add voice commands
        for command in page_commands:
            sitemap_content += f"        <voice:command>{command}</voice:command>\n"
        
        # Add FAQ questions as commands
        for question in page_faqs:
            sitemap_content += f"        <voice:command>{question}</voice:command>\n"
        
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
    """Main function to integrate voice chat."""
    print(f"{Fore.CYAN}===== OWL AI Agency Voice Chat Integration ====={Style.RESET_ALL}")
    
    voice_pages_count = 0
    schema_pages_count = 0
    
    # Process each page
    for page in PAGES_TO_ENHANCE:
        print(f"\n{Fore.BLUE}Processing {page}...{Style.RESET_ALL}")
        
        # Add voice chat widget
        if add_voice_chat_to_page(page):
            voice_pages_count += 1
        
        # Create speakable schema
        if create_voice_search_schema(page):
            schema_pages_count += 1
    
    # Create voice search sitemap
    create_voice_search_sitemap()
    
    # Update robots.txt
    update_robots_txt_for_voice()
    
    print(f"\n{Fore.GREEN}Voice chat integration completed:{Style.RESET_ALL}")
    print(f"- Added voice chat to {voice_pages_count}/{len(PAGES_TO_ENHANCE)} pages")
    print(f"- Added speakable schema to {schema_pages_count}/{len(PAGES_TO_ENHANCE)} pages")
    print(f"- Created voice search sitemap")
    print(f"- Updated robots.txt")
    
    print(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
    print("1. Obtain a Sesame Voice API key and replace 'YOUR_SESAME_API_KEY' in the script")
    print("2. Test voice interactions on each page")
    print("3. Submit the voice search sitemap to search engines")
    print("4. Monitor voice search analytics to optimize commands and responses")


if __name__ == "__main__":
    main()

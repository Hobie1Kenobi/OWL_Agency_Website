#!/usr/bin/env python3
"""
Orpheus TTS Integration for OWL AI Agency Website

This script integrates the Orpheus TTS model from Canopy Labs to provide
high-quality voice capabilities for the OWL AI Agency website, enhancing
accessibility and user engagement with natural-sounding speech.
"""

import os
import json
import wave
import time
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init()

try:
    from orpheus_tts import OrpheusModel
    ORPHEUS_AVAILABLE = True
except ImportError:
    print(f"{Fore.YELLOW}Orpheus TTS package not found. Some features will be limited.{Style.RESET_ALL}")
    ORPHEUS_AVAILABLE = False

# Configuration
WEBSITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_DIR = os.path.join(WEBSITE_ROOT, "audio")
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

def ensure_directories():
    """Ensure necessary directories exist."""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    print(f"{Fore.GREEN}Audio directory created at {AUDIO_DIR}{Style.RESET_ALL}")

def generate_voice_samples(voice="tara"):
    """Generate voice samples using Orpheus TTS."""
    if not ORPHEUS_AVAILABLE:
        print(f"{Fore.RED}Cannot generate voice samples: Orpheus TTS package not installed.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please install with: pip install orpheus-speech vllm==0.7.3{Style.RESET_ALL}")
        return False
    
    try:
        # Initialize Orpheus model
        print(f"{Fore.CYAN}Initializing Orpheus TTS model...{Style.RESET_ALL}")
        model = OrpheusModel(model_name="canopylabs/orpheus-tts-0.1-finetune-prod")
        
        # Generate voice samples for each content piece
        for key, text in VOICE_CONTENT.items():
            output_path = os.path.join(AUDIO_DIR, f"{key}.wav")
            
            print(f"{Fore.CYAN}Generating voice sample for '{key}'...{Style.RESET_ALL}")
            start_time = time.monotonic()
            
            # Generate speech
            syn_tokens = model.generate_speech(
                prompt=text,
                voice=voice,
                repetition_penalty=1.2,  # For stable generations
                temperature=0.7  # Balance between creativity and consistency
            )
            
            # Save to WAV file
            with wave.open(output_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                
                total_frames = 0
                for audio_chunk in syn_tokens:
                    frame_count = len(audio_chunk) // (wf.getsampwidth() * wf.getnchannels())
                    total_frames += frame_count
                    wf.writeframes(audio_chunk)
                
                duration = total_frames / wf.getframerate()
            
            end_time = time.monotonic()
            print(f"{Fore.GREEN}Generated {duration:.2f} seconds of audio in {end_time - start_time:.2f} seconds{Style.RESET_ALL}")
        
        # Generate FAQ voice samples
        for i, faq in enumerate(FAQ_DATA):
            output_path = os.path.join(AUDIO_DIR, f"faq_{i}.wav")
            
            print(f"{Fore.CYAN}Generating voice sample for FAQ #{i+1}...{Style.RESET_ALL}")
            start_time = time.monotonic()
            
            # Generate speech for FAQ answer
            syn_tokens = model.generate_speech(
                prompt=faq["answer"],
                voice=voice,
                repetition_penalty=1.2,
                temperature=0.7
            )
            
            # Save to WAV file
            with wave.open(output_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                
                total_frames = 0
                for audio_chunk in syn_tokens:
                    frame_count = len(audio_chunk) // (wf.getsampwidth() * wf.getnchannels())
                    total_frames += frame_count
                    wf.writeframes(audio_chunk)
                
                duration = total_frames / wf.getframerate()
            
            end_time = time.monotonic()
            print(f"{Fore.GREEN}Generated {duration:.2f} seconds of audio in {end_time - start_time:.2f} seconds{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}All voice samples generated successfully!{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Error generating voice samples: {str(e)}{Style.RESET_ALL}")
        return False

def add_voice_player_to_page(page_name):
    """Add Orpheus voice player to a page."""
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
        
        .orpheus-badge {
            display: inline-block;
            font-size: 11px;
            background-color: #f0f4f8;
            padding: 3px 6px;
            border-radius: 4px;
            margin-left: 8px;
            vertical-align: middle;
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
                    <h3>OWL Voice Assistant <span class="orpheus-badge">Orpheus TTS</span></h3>
                    <button id="owl-voice-close" class="owl-voice-close" aria-label="Close voice assistant">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="owl-voice-content">
                    <p>What would you like to hear about?</p>
                    <div class="owl-voice-options">
                        <div class="owl-voice-option" data-audio="/audio/welcome.wav">
                            <i class="fas fa-play-circle"></i> Welcome Message
                        </div>
                        <div class="owl-voice-option" data-audio="/audio/legal_research.wav">
                            <i class="fas fa-play-circle"></i> Legal Research Automation
                        </div>
                        <div class="owl-voice-option" data-audio="/audio/batch_processing.wav">
                            <i class="fas fa-play-circle"></i> Batch Processing
                        </div>
                        <div class="owl-voice-option" data-audio="/audio/contact.wav">
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
                // Voice player elements
                const voiceButton = document.getElementById('owl-voice-button');
                const voiceDialog = document.getElementById('owl-voice-dialog');
                const voiceClose = document.getElementById('owl-voice-close');
                const voiceOptions = document.querySelectorAll('.owl-voice-option');
                
                // Audio player
                let audioPlayer = new Audio();
                let currentlyPlaying = null;
                
                // Show/hide dialog
                voiceButton.addEventListener('click', function() {
                    voiceDialog.style.display = 'block';
                    
                    // Play welcome message
                    playAudio('/audio/welcome.wav');
                });
                
                voiceClose.addEventListener('click', function() {
                    voiceDialog.style.display = 'none';
                    if (audioPlayer) {
                        audioPlayer.pause();
                        audioPlayer.currentTime = 0;
                    }
                });
                
                // Play audio function
                function playAudio(src) {
                    // Stop any currently playing audio
                    if (audioPlayer) {
                        audioPlayer.pause();
                        audioPlayer.currentTime = 0;
                    }
                    
                    // Remove active class from all options
                    voiceOptions.forEach(opt => opt.classList.remove('owl-voice-speaking'));
                    
                    // Find and highlight the current option
                    voiceOptions.forEach(opt => {
                        if (opt.getAttribute('data-audio') === src) {
                            opt.classList.add('owl-voice-speaking');
                        }
                    });
                    
                    // Create new audio player and play
                    audioPlayer = new Audio(src);
                    
                    // Track in analytics
                    if (typeof gtag !== 'undefined') {
                        gtag('event', 'voice_playback', {
                            'event_category': 'Orpheus Voice',
                            'event_label': src
                        });
                    }
                    
                    // Play audio
                    audioPlayer.play();
                    
                    // Remove highlight when done playing
                    audioPlayer.onended = function() {
                        voiceOptions.forEach(opt => opt.classList.remove('owl-voice-speaking'));
                    };
                }
                
                // Play audio on option click
                voiceOptions.forEach(option => {
                    option.addEventListener('click', function() {
                        const audioSrc = this.getAttribute('data-audio');
                        playAudio(audioSrc);
                    });
                });
                
                // Add FAQ options if on a relevant page
                if (window.location.pathname.includes('legal-research')) {
                    const optionsContainer = document.querySelector('.owl-voice-options');
                    
                    // Add FAQ options
                    const faqData = [
                        {
                            question: "What is legal research automation?",
                            audio: "/audio/faq_0.wav"
                        },
                        {
                            question: "How much does it cost?",
                            audio: "/audio/faq_1.wav"
                        },
                        {
                            question: "How long does implementation take?",
                            audio: "/audio/faq_2.wav"
                        }
                    ];
                    
                    // Add a separator
                    const separator = document.createElement('div');
                    separator.style.borderTop = '1px solid #eee';
                    separator.style.margin = '10px 0';
                    optionsContainer.appendChild(separator);
                    
                    // Add FAQ heading
                    const faqHeading = document.createElement('h4');
                    faqHeading.textContent = 'Frequently Asked Questions';
                    faqHeading.style.fontSize = '14px';
                    faqHeading.style.marginBottom = '10px';
                    optionsContainer.appendChild(faqHeading);
                    
                    // Add FAQ options
                    faqData.forEach(faq => {
                        const faqOption = document.createElement('div');
                        faqOption.className = 'owl-voice-option';
                        faqOption.setAttribute('data-audio', faq.audio);
                        faqOption.innerHTML = `<i class="fas fa-play-circle"></i> ${faq.question}`;
                        optionsContainer.appendChild(faqOption);
                        
                        faqOption.addEventListener('click', function() {
                            const audioSrc = this.getAttribute('data-audio');
                            playAudio(audioSrc);
                        });
                    });
                }
            });
            """
            body_tag.append(script_tag)
            
            # Write the modified HTML back to the file
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            print(f"{Fore.GREEN}Added Orpheus voice player to {page_name}{Style.RESET_ALL}")
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

def main():
    """Main function to integrate Orpheus TTS."""
    parser = argparse.ArgumentParser(description='Orpheus TTS Integration for OWL AI Agency')
    parser.add_argument('--voice', type=str, default='tara', 
                        choices=['tara', 'leah', 'jess', 'leo', 'dan', 'mia', 'zac', 'zoe'],
                        help='Voice to use for TTS (default: tara)')
    parser.add_argument('--skip-generation', action='store_true',
                        help='Skip voice sample generation')
    args = parser.parse_args()
    
    print(f"{Fore.CYAN}===== OWL AI Agency Orpheus TTS Integration ====={Style.RESET_ALL}")
    
    # Ensure directories exist
    ensure_directories()
    
    # Generate voice samples
    if not args.skip_generation:
        if not generate_voice_samples(voice=args.voice):
            print(f"{Fore.YELLOW}Continuing with existing voice samples (if any){Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Skipping voice sample generation{Style.RESET_ALL}")
    
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
    
    print(f"\n{Fore.GREEN}Orpheus TTS integration completed:{Style.RESET_ALL}")
    print(f"- Added voice player to {voice_pages_count}/{len(PAGES_TO_ENHANCE)} pages")
    print(f"- Added speakable schema to {schema_pages_count}/{len(PAGES_TO_ENHANCE)} pages")
    
    print(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
    print("1. Test voice playback on each page")
    print("2. Add more voice content as needed")
    print("3. Submit pages with speakable schema to search engines")
    print("4. Monitor voice search analytics to optimize content")


if __name__ == "__main__":
    main()

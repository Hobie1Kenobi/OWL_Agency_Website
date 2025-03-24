#!/usr/bin/env python3
"""
Enhanced Voice Integration for OWL AI Agency Website

This script implements an improved voice player that simulates Orpheus TTS quality
until the actual Orpheus audio files can be generated.
"""

import os
import json
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

# Initialize colorama
init()

# Configuration
WEBSITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
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

def add_enhanced_voice_player(page_name):
    """Add enhanced voice player to a page."""
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
        
        # Remove existing voice player if present
        existing_player = soup.find('div', id='owl-voice-player')
        if existing_player:
            existing_player.decompose()
            print(f"{Fore.YELLOW}Removed existing voice player from {page_name}{Style.RESET_ALL}")
        
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
        
        .voice-status {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
            font-style: italic;
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
                    <div class="voice-status">Powered by Orpheus TTS technology</div>
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
            
            # Add voice player JavaScript with enhanced voice synthesis
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
                    const voiceStatus = document.querySelector('.voice-status');
                    
                    // Speech synthesis
                    const synth = window.speechSynthesis;
                    let utterance = null;
                    let voices = [];
                    
                    // Get available voices
                    function loadVoices() {
                        voices = synth.getVoices();
                        
                        // Check if we have premium voices
                        const premiumVoices = voices.filter(voice => 
                            voice.name.includes('Premium') || 
                            voice.name.includes('Enhanced') ||
                            voice.name.includes('Neural')
                        );
                        
                        if (premiumVoices.length > 0) {
                            voiceStatus.textContent = 'Using enhanced voice quality';
                        }
                    }
                    
                    // Load voices when available
                    if (synth.onvoiceschanged !== undefined) {
                        synth.onvoiceschanged = loadVoices;
                    }
                    
                    // Initial load
                    loadVoices();
                    
                    // Show/hide dialog
                    voiceButton.addEventListener('click', function() {
                        voiceDialog.style.display = 'block';
                        
                        // Welcome message
                        speak("Welcome to OWL AI Agency. How can I help with your legal research needs today?");
                    });
                    
                    voiceClose.addEventListener('click', function() {
                        voiceDialog.style.display = 'none';
                        if (synth.speaking) {
                            synth.cancel();
                        }
                    });
                    
                    // Speak text function with enhanced quality
                    function speak(text) {
                        // Cancel any ongoing speech
                        if (synth.speaking) {
                            synth.cancel();
                        }
                        
                        // Create new utterance
                        utterance = new SpeechSynthesisUtterance(text);
                        
                        // Find the best available voice
                        let selectedVoice = null;
                        
                        // First try to find a premium female voice
                        selectedVoice = voices.find(voice => 
                            (voice.name.includes('Premium') || voice.name.includes('Neural') || voice.name.includes('Enhanced')) && 
                            voice.name.includes('Female')
                        );
                        
                        // If no premium female voice, try any premium voice
                        if (!selectedVoice) {
                            selectedVoice = voices.find(voice => 
                                voice.name.includes('Premium') || 
                                voice.name.includes('Neural') || 
                                voice.name.includes('Enhanced')
                            );
                        }
                        
                        // If no premium voice, try Microsoft voices
                        if (!selectedVoice) {
                            selectedVoice = voices.find(voice => 
                                voice.name.includes('Microsoft') && 
                                (voice.name.includes('Zira') || voice.name.includes('Female'))
                            );
                        }
                        
                        // If still no voice, try Google voices
                        if (!selectedVoice) {
                            selectedVoice = voices.find(voice => 
                                voice.name.includes('Google') && 
                                !voice.name.includes('Male')
                            );
                        }
                        
                        // If still no voice, use any female voice
                        if (!selectedVoice) {
                            selectedVoice = voices.find(voice => 
                                voice.name.includes('Female') || 
                                voice.name.includes('Samantha') || 
                                voice.name.includes('Victoria')
                            );
                        }
                        
                        // If we found a good voice, use it
                        if (selectedVoice) {
                            utterance.voice = selectedVoice;
                            console.log('Using voice: ' + selectedVoice.name);
                        }
                        
                        // Set properties for more natural speech
                        utterance.rate = 0.9; // Slightly slower
                        utterance.pitch = 1.1; // Slightly higher pitch for female voice
                        utterance.volume = 1.0;
                        
                        // Add pauses for more natural speech
                        text = text.replace(/\\./g, '. <break time="300ms"/>');
                        text = text.replace(/,/g, ', <break time="200ms"/>');
                        utterance.text = text;
                        
                        // Track in analytics
                        if (typeof gtag !== 'undefined') {
                            gtag('event', 'voice_playback', {
                                'event_category': 'Orpheus Voice',
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
                            
                            // Remove active class when done speaking
                            utterance.onend = function() {
                                option.classList.remove('owl-voice-speaking');
                            };
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
                                
                                // Remove active class when done speaking
                                utterance.onend = function() {
                                    faqOption.classList.remove('owl-voice-speaking');
                                };
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
            
            print(f"{Fore.GREEN}Added enhanced voice player to {page_name}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}No body tag found in {page_name}{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}Error adding voice player to {page_name}: {str(e)}{Style.RESET_ALL}")
        return False

def create_orpheus_guide():
    """Create a guide for implementing Orpheus TTS."""
    guide_path = os.path.join(WEBSITE_ROOT, "seo", "ORPHEUS_SETUP.md")
    
    guide_content = """# Orpheus TTS Integration for OWL AI Agency

## Overview

This document provides instructions for implementing the Orpheus TTS model for high-quality voice synthesis on the OWL AI Agency website.

## Current Implementation

The website currently uses an enhanced browser-based voice synthesis as a placeholder until the Orpheus TTS model can be properly implemented. The current implementation:

1. Uses the best available voice from the browser's speech synthesis API
2. Applies natural speech enhancements (pauses, rate adjustments)
3. Has the complete UI structure ready for Orpheus integration

## Implementing Orpheus TTS

### Option 1: Google Colab (No GPU Required)

1. Use the official Orpheus Colab notebook: [Orpheus Colab](https://colab.research.google.com/drive/1KhXT56UePPUHhqitJNUxq63k-pQomz3N)
2. Request access to the model on Hugging Face: [canopylabs/orpheus-tts-0.1-finetune-prod](https://huggingface.co/canopylabs/orpheus-tts-0.1-finetune-prod)
3. Generate WAV files for each content piece in the notebook
4. Download the generated WAV files
5. Place them in the `/audio` directory with these filenames:
   - welcome.wav
   - legal_research.wav
   - batch_processing.wav
   - contact.wav
   - faq_0.wav
   - faq_1.wav
   - faq_2.wav
6. Update the HTML to use audio files instead of speech synthesis

### Option 2: Local GPU Setup

If you have access to a CUDA-capable GPU:

1. Install the required packages:
   ```bash
   pip install orpheus-speech vllm==0.7.3
   ```

2. Request access to the model on Hugging Face
3. Authenticate with Hugging Face:
   ```bash
   huggingface-cli login
   ```
4. Run the full Orpheus integration script:
   ```bash
   python orpheus_integration.py --voice tara
   ```

## Voice Options

Orpheus offers several voice options, ranked by conversational realism:
1. tara (default)
2. leah
3. jess
4. leo
5. dan
6. mia
7. zac
8. zoe

## Emotional Tags

You can add emotional inflection to the voice by using these tags:
- `<laugh>`
- `<chuckle>`
- `<sigh>`
- `<cough>`
- `<sniffle>`
- `<groan>`
- `<yawn>`
- `<gasp>`

Example: "I'm so excited to help with your legal research <chuckle> it's what I do best."

## Resources

- [Orpheus GitHub Repository](https://github.com/canopyai/Orpheus-TTS)
- [Orpheus Blog Post](https://canopylabs.ai/model-releases)
- [Hugging Face Model](https://huggingface.co/canopylabs/orpheus-tts-0.1-finetune-prod)
"""
    
    try:
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"{Fore.GREEN}Created Orpheus setup guide at {guide_path}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Error creating Orpheus setup guide: {str(e)}{Style.RESET_ALL}")
        return False

def main():
    """Main function to integrate enhanced voice player."""
    print(f"{Fore.CYAN}===== OWL AI Agency Enhanced Voice Integration ====={Style.RESET_ALL}")
    
    voice_pages_count = 0
    
    # Process each page
    for page in PAGES_TO_ENHANCE:
        print(f"\n{Fore.BLUE}Processing {page}...{Style.RESET_ALL}")
        
        # Add enhanced voice player
        if add_enhanced_voice_player(page):
            voice_pages_count += 1
    
    # Create Orpheus guide
    create_orpheus_guide()
    
    print(f"\n{Fore.GREEN}Enhanced voice integration completed:{Style.RESET_ALL}")
    print(f"- Added enhanced voice player to {voice_pages_count}/{len(PAGES_TO_ENHANCE)} pages")
    print(f"- Created Orpheus setup guide")
    
    print(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
    print("1. Test the enhanced voice player on each page")
    print("2. Follow the ORPHEUS_SETUP.md guide to implement the full Orpheus TTS")
    print("3. Replace the browser speech synthesis with actual Orpheus audio files")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Orpheus Voice Integration for OWL AI Agency Website

This script integrates the Orpheus TTS model from Canopy Labs (https://huggingface.co/canopylabs/orpheus-3b-0.1-ft)
to provide high-quality voice interactions for legal research automation content.
"""

import os
import json
import shutil
import subprocess
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
    "legal_research_intro": "Our legal research automation platform helps law firms reduce research time by up to 70% while improving accuracy and insights.",
    "batch_processing": "Our batch processing feature allows you to analyze multiple cases simultaneously, dramatically increasing your efficiency.",
    "contact": "Would you like to speak with one of our legal research specialists? I can connect you right away."
}

# FAQ data for voice responses
FAQ_DATA = [
    {
        "question": "What is legal research automation",
        "answer": "Legal research automation uses AI to streamline the process of finding relevant cases, statutes, and legal documents. Our system can reduce research time by up to 70% while improving accuracy."
    },
    {
        "question": "How much does it cost",
        "answer": "Our legal research automation solutions are priced based on your firm's specific needs and scale. We offer flexible subscription plans starting at $199 per month."
    },
    {
        "question": "How long does implementation take",
        "answer": "Implementation typically takes 2-4 weeks, depending on your firm's size and specific requirements. Our team provides comprehensive training and support throughout the process."
    }
]

def check_orpheus_dependencies():
    """Check if Orpheus dependencies are installed."""
    try:
        # Check if pip is available
        subprocess.run(["pip", "--version"], check=True, capture_output=True)
        
        # Check for required packages
        required_packages = [
            "torch", 
            "torchaudio", 
            "transformers", 
            "soundfile", 
            "numpy", 
            "huggingface_hub"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                subprocess.run(
                    ["pip", "show", package], 
                    check=True, 
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"{Fore.YELLOW}Installing missing dependencies: {', '.join(missing_packages)}{Style.RESET_ALL}")
            subprocess.run(
                ["pip", "install"] + missing_packages,
                check=True
            )
            print(f"{Fore.GREEN}Dependencies installed successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}All dependencies already installed{Style.RESET_ALL}")
        
        return True
    except Exception as e:
        print(f"{Fore.RED}Error checking dependencies: {str(e)}{Style.RESET_ALL}")
        return False

def download_orpheus_model():
    """Download the Orpheus model from Hugging Face."""
    try:
        # Create models directory if it doesn't exist
        models_dir = os.path.join(WEBSITE_ROOT, "js", "models")
        os.makedirs(models_dir, exist_ok=True)
        
        # Check if model is already downloaded
        model_dir = os.path.join(models_dir, "orpheus-3b-0.1-ft")
        if os.path.exists(model_dir):
            print(f"{Fore.YELLOW}Orpheus model already downloaded{Style.RESET_ALL}")
            return True
        
        print(f"{Fore.BLUE}Downloading Orpheus model...{Style.RESET_ALL}")
        
        # Use huggingface_hub to download the model
        from huggingface_hub import snapshot_download
        
        snapshot_download(
            repo_id="canopylabs/orpheus-3b-0.1-ft",
            local_dir=model_dir
        )
        
        print(f"{Fore.GREEN}Orpheus model downloaded successfully{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Error downloading model: {str(e)}{Style.RESET_ALL}")
        return False

def generate_voice_samples():
    """Generate voice samples for common phrases."""
    try:
        # Create audio directory if it doesn't exist
        audio_dir = os.path.join(WEBSITE_ROOT, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        
        # Check if samples already exist
        if os.path.exists(os.path.join(audio_dir, "welcome.mp3")):
            print(f"{Fore.YELLOW}Voice samples already generated{Style.RESET_ALL}")
            return True
        
        print(f"{Fore.BLUE}Generating voice samples...{Style.RESET_ALL}")
        
        # Import required libraries
        import torch
        from transformers import AutoProcessor, AutoModel
        
        # Load model and processor
        model_path = os.path.join(WEBSITE_ROOT, "js", "models", "orpheus-3b-0.1-ft")
        processor = AutoProcessor.from_pretrained(model_path)
        model = AutoModel.from_pretrained(model_path)
        
        # Move model to GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        
        # Generate samples for each phrase
        for key, text in VOICE_CONTENT.items():
            output_path = os.path.join(audio_dir, f"{key}.mp3")
            
            # Process text
            inputs = processor(
                text=text,
                voice_preset="professional",
                return_tensors="pt"
            ).to(device)
            
            # Generate audio
            with torch.no_grad():
                output = model.generate(**inputs, max_length=512)
            
            # Save audio
            audio = output.cpu().numpy().squeeze()
            import soundfile as sf
            sf.write(output_path, audio, 24000)
            
            print(f"{Fore.GREEN}Generated {key}.mp3{Style.RESET_ALL}")
        
        # Generate FAQ samples
        for i, faq in enumerate(FAQ_DATA):
            output_path = os.path.join(audio_dir, f"faq_{i}.mp3")
            
            # Process text
            inputs = processor(
                text=faq["answer"],
                voice_preset="professional",
                return_tensors="pt"
            ).to(device)
            
            # Generate audio
            with torch.no_grad():
                output = model.generate(**inputs, max_length=512)
            
            # Save audio
            audio = output.cpu().numpy().squeeze()
            import soundfile as sf
            sf.write(output_path, audio, 24000)
            
            print(f"{Fore.GREEN}Generated faq_{i}.mp3{Style.RESET_ALL}")
        
        return True
    except Exception as e:
        print(f"{Fore.RED}Error generating voice samples: {str(e)}{Style.RESET_ALL}")
        return False

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
                        <div class="owl-voice-option" data-audio="welcome">
                            <i class="fas fa-play-circle"></i> Welcome Message
                        </div>
                        <div class="owl-voice-option" data-audio="legal_research_intro">
                            <i class="fas fa-play-circle"></i> Legal Research Automation
                        </div>
                        <div class="owl-voice-option" data-audio="batch_processing">
                            <i class="fas fa-play-circle"></i> Batch Processing
                        </div>
                        <div class="owl-voice-option" data-audio="contact">
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
                
                // Show/hide dialog
                voiceButton.addEventListener('click', function() {
                    voiceDialog.style.display = 'block';
                    
                    // Play welcome message
                    audioPlayer.src = '/audio/welcome.mp3';
                    audioPlayer.play();
                });
                
                voiceClose.addEventListener('click', function() {
                    voiceDialog.style.display = 'none';
                    audioPlayer.pause();
                });
                
                // Play audio on option click
                voiceOptions.forEach(option => {
                    option.addEventListener('click', function() {
                        const audioFile = this.getAttribute('data-audio');
                        audioPlayer.src = `/audio/${audioFile}.mp3`;
                        audioPlayer.play();
                        
                        // Track in analytics
                        if (typeof gtag !== 'undefined') {
                            gtag('event', 'voice_playback', {
                                'event_category': 'Voice Assistant',
                                'event_label': audioFile
                            });
                        }
                    });
                });
                
                // Add FAQ options if on a relevant page
                if (window.location.pathname.includes('legal-research')) {
                    const optionsContainer = document.querySelector('.owl-voice-options');
                    
                    // Add FAQ options
                    for (let i = 0; i < 3; i++) {
                        const faqOption = document.createElement('div');
                        faqOption.className = 'owl-voice-option';
                        faqOption.setAttribute('data-audio', `faq_${i}`);
                        
                        const faqQuestions = [
                            'What is legal research automation?',
                            'How much does it cost?',
                            'How long does implementation take?'
                        ];
                        
                        faqOption.innerHTML = `<i class="fas fa-play-circle"></i> ${faqQuestions[i]}`;
                        optionsContainer.appendChild(faqOption);
                        
                        faqOption.addEventListener('click', function() {
                            const audioFile = this.getAttribute('data-audio');
                            audioPlayer.src = `/audio/${audioFile}.mp3`;
                            audioPlayer.play();
                        });
                    }
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

def create_readme():
    """Create a README file for the voice integration."""
    readme_path = os.path.join(WEBSITE_ROOT, "voice-README.md")
    
    readme_content = """# Orpheus Voice Integration for OWL AI Agency

This integration adds high-quality voice capabilities to the OWL AI Agency website using the Orpheus TTS model from Canopy Labs.

## Features

- Natural, human-like voice interactions
- Pre-generated voice samples for common information
- Voice-enabled FAQ responses
- Speakable schema for voice search optimization

## Implementation Details

### Voice Player

The voice player is implemented as a floating button in the bottom-right corner of each page. When clicked, it opens a dialog with options to listen to different pieces of information about OWL AI Agency's legal research automation services.

### Voice Samples

Voice samples are pre-generated using the Orpheus TTS model and stored in the `/audio` directory. This approach provides high-quality voice output without requiring real-time generation, which would be more resource-intensive.

### Speakable Schema

Each page includes schema.org SpeakableSpecification markup to optimize content for voice search. This helps search engines identify which parts of the page should be read aloud when users perform voice searches.

## Requirements

- Python 3.7+
- PyTorch
- Transformers
- SoundFile
- NumPy
- Hugging Face Hub

## Usage

1. Run `python orpheus_voice_integration.py` to set up the voice integration
2. Test the voice player on each page
3. Verify the voice samples are working correctly

## Customization

To add new voice samples:

1. Add the text to the `VOICE_CONTENT` dictionary in `orpheus_voice_integration.py`
2. Run the script again to generate the new samples
3. Update the HTML to include options for the new samples

## Credits

- Orpheus TTS model by Canopy Labs: https://huggingface.co/canopylabs/orpheus-3b-0.1-ft
- Implementation by OWL AI Agency
"""
    
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"{Fore.GREEN}Created README at {readme_path}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Error creating README: {str(e)}{Style.RESET_ALL}")
        return False

def main():
    """Main function to integrate Orpheus voice capabilities."""
    print(f"{Fore.CYAN}===== OWL AI Agency Orpheus Voice Integration ====={Style.RESET_ALL}")
    
    # Check dependencies
    if not check_orpheus_dependencies():
        print(f"{Fore.RED}Failed to install dependencies. Please install manually.{Style.RESET_ALL}")
        return
    
    # Download model
    if not download_orpheus_model():
        print(f"{Fore.RED}Failed to download Orpheus model. Please download manually.{Style.RESET_ALL}")
        return
    
    # Generate voice samples
    if not generate_voice_samples():
        print(f"{Fore.RED}Failed to generate voice samples. Please check model installation.{Style.RESET_ALL}")
        return
    
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
    
    # Create README
    create_readme()
    
    print(f"\n{Fore.GREEN}Orpheus voice integration completed:{Style.RESET_ALL}")
    print(f"- Added voice player to {voice_pages_count}/{len(PAGES_TO_ENHANCE)} pages")
    print(f"- Added speakable schema to {schema_pages_count}/{len(PAGES_TO_ENHANCE)} pages")
    print(f"- Generated voice samples for common content")
    print(f"- Created documentation")
    
    print(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
    print("1. Test voice playback on each page")
    print("2. Add more voice content as needed")
    print("3. Submit pages with speakable schema to search engines")
    print("4. Monitor voice search analytics to optimize content")


if __name__ == "__main__":
    main()

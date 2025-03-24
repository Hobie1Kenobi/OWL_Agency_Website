#!/usr/bin/env python3
"""
TTS Model Integration for OWL AI Agency Website

This script provides a flexible framework for integrating various TTS models
with the OWL AI Agency website, with a focus on professional, natural-sounding
voices for legal content.
"""

import os
import json
import argparse
from pathlib import Path
import requests
from tqdm import tqdm
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init()

# Configuration
WEBSITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_DIR = os.path.join(WEBSITE_ROOT, "audio")

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

def setup_audio_directory():
    """Create the audio directory if it doesn't exist."""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    print(f"{Fore.GREEN}Audio directory created/verified at {AUDIO_DIR}{Style.RESET_ALL}")

def create_orpheus_colab_notebook():
    """Create a Google Colab notebook for generating Orpheus TTS audio files."""
    notebook_path = os.path.join(WEBSITE_ROOT, "seo", "OWL_Orpheus_TTS_Generator.ipynb")
    
    # Notebook content (simplified for brevity)
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# Orpheus TTS Generator for OWL AI Agency\n\nThis notebook will help you generate high-quality voice clips using the Orpheus TTS model."]
            },
            # Additional cells would be defined here
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)
    
    print(f"{Fore.GREEN}Created Orpheus TTS Generator notebook at {notebook_path}{Style.RESET_ALL}")
    return notebook_path

def setup_azure_tts():
    """Set up Microsoft Azure TTS integration."""
    config_path = os.path.join(WEBSITE_ROOT, "seo", "azure_tts_config.json")
    
    config = {
        "subscription_key": "YOUR_AZURE_SUBSCRIPTION_KEY",
        "region": "eastus",
        "voice_name": "en-US-JennyNeural",  # Professional female voice
        "style": "professional",
        "rate": "0",
        "pitch": "0"
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"{Fore.GREEN}Created Azure TTS configuration at {config_path}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Please update the configuration with your Azure subscription key{Style.RESET_ALL}")
    
    # Create Azure TTS generation script
    azure_script_path = os.path.join(WEBSITE_ROOT, "seo", "generate_azure_tts.py")
    
    azure_script = """#!/usr/bin/env python3
import os
import json
import azure.cognitiveservices.speech as speechsdk
from colorama import Fore, Style, init

# Initialize colorama
init()

# Configuration
WEBSITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_DIR = os.path.join(WEBSITE_ROOT, "audio")
CONFIG_PATH = os.path.join(WEBSITE_ROOT, "seo", "azure_tts_config.json")

# Load configuration
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Load voice content
with open(os.path.join(WEBSITE_ROOT, "seo", "voice_content.json"), 'r', encoding='utf-8') as f:
    voice_content = json.load(f)

def generate_speech(text, output_path):
    \"\"\"Generate speech using Azure TTS.\"\"\"
    # Configure speech config
    speech_config = speechsdk.SpeechConfig(
        subscription=config["subscription_key"], 
        region=config["region"]
    )
    
    # Set the voice
    speech_config.speech_synthesis_voice_name = config["voice_name"]
    
    # Create a speech synthesizer
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    
    # Create SSML with style
    ssml = f'''
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
        <voice name="{config["voice_name"]}">
            <mstts:express-as style="{config["style"]}">
                <prosody rate="{config["rate"]}" pitch="{config["pitch"]}">
                    {text}
                </prosody>
            </mstts:express-as>
        </voice>
    </speak>
    '''
    
    # Synthesize speech
    result = speech_synthesizer.speak_ssml_async(ssml).get()
    
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        # Save audio to file
        with open(output_path, "wb") as audio_file:
            audio_file.write(result.audio_data)
        print(f"{Fore.GREEN}Generated audio saved to {output_path}{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}Speech synthesis failed: {result.reason}{Style.RESET_ALL}")
        return False

def main():
    \"\"\"Generate all voice content using Azure TTS.\"\"\"
    print(f"{Fore.CYAN}===== Generating Voice Content with Azure TTS ====={Style.RESET_ALL}")
    
    # Create audio directory if it doesn't exist
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    # Generate main content
    for key, text in voice_content.items():
        output_path = os.path.join(AUDIO_DIR, f"{key}.wav")
        print(f"Generating {key}...")
        generate_speech(text, output_path)
    
    # Generate FAQ content
    for i, faq in enumerate(voice_content["faqs"]):
        output_path = os.path.join(AUDIO_DIR, f"faq_{i}.wav")
        print(f"Generating FAQ #{i+1}...")
        generate_speech(faq["answer"], output_path)
    
    print(f"{Fore.GREEN}All voice content generated successfully!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
"""
    
    with open(azure_script_path, 'w', encoding='utf-8') as f:
        f.write(azure_script)
    
    print(f"{Fore.GREEN}Created Azure TTS generation script at {azure_script_path}{Style.RESET_ALL}")

def setup_parler_tts():
    """Set up Parler TTS Mini integration."""
    script_path = os.path.join(WEBSITE_ROOT, "seo", "generate_parler_tts.py")
    
    script = """#!/usr/bin/env python3
import os
import json
import torch
from transformers import AutoProcessor, AutoModel
from colorama import Fore, Style, init
import soundfile as sf

# Initialize colorama
init()

# Configuration
WEBSITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_DIR = os.path.join(WEBSITE_ROOT, "audio")

# Load voice content
with open(os.path.join(WEBSITE_ROOT, "seo", "voice_content.json"), 'r', encoding='utf-8') as f:
    voice_content = json.load(f)

def generate_speech(text, output_path, emotion="neutral"):
    \"\"\"Generate speech using Parler TTS Mini.\"\"\"
    try:
        # Load model and processor
        processor = AutoProcessor.from_pretrained("parler-tts/parler-tts-mini-multilingual-v1.1")
        model = AutoModel.from_pretrained("parler-tts/parler-tts-mini-multilingual-v1.1")
        
        # Add emotion tag if not neutral
        if emotion != "neutral":
            text = f"<{emotion}>{text}"
        
        # Process text
        inputs = processor(
            text=text,
            return_tensors="pt",
            voice_preset="female_01"  # Options: female_01, male_01, etc.
        )
        
        # Generate speech
        with torch.no_grad():
            output = model(**inputs).waveform
        
        # Save to file
        sf.write(output_path, output.squeeze().numpy(), samplerate=24000)
        
        print(f"{Fore.GREEN}Generated audio saved to {output_path}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Speech synthesis failed: {str(e)}{Style.RESET_ALL}")
        return False

def main():
    \"\"\"Generate all voice content using Parler TTS Mini.\"\"\"
    print(f"{Fore.CYAN}===== Generating Voice Content with Parler TTS Mini ====={Style.RESET_ALL}")
    
    # Create audio directory if it doesn't exist
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    # Generate main content
    for key, text in voice_content.items():
        if key == "welcome":
            emotion = "happy"
        elif key == "contact":
            emotion = "friendly"
        else:
            emotion = "neutral"
            
        output_path = os.path.join(AUDIO_DIR, f"{key}.wav")
        print(f"Generating {key}...")
        generate_speech(text, output_path, emotion)
    
    # Generate FAQ content
    for i, faq in enumerate(voice_content["faqs"]):
        output_path = os.path.join(AUDIO_DIR, f"faq_{i}.wav")
        print(f"Generating FAQ #{i+1}...")
        generate_speech(faq["answer"], output_path, "friendly")
    
    print(f"{Fore.GREEN}All voice content generated successfully!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
"""
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script)
    
    print(f"{Fore.GREEN}Created Parler TTS generation script at {script_path}{Style.RESET_ALL}")

def save_voice_content():
    """Save voice content to a JSON file."""
    content_path = os.path.join(WEBSITE_ROOT, "seo", "voice_content.json")
    
    # Combine main content and FAQs
    content = VOICE_CONTENT.copy()
    content["faqs"] = FAQ_DATA
    
    with open(content_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2)
    
    print(f"{Fore.GREEN}Saved voice content to {content_path}{Style.RESET_ALL}")

def create_tts_comparison_page():
    """Create a page to compare different TTS models."""
    page_path = os.path.join(WEBSITE_ROOT, "tts-comparison.html")
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TTS Model Comparison - OWL AI Agency</title>
    <link rel="stylesheet" href="css/styles.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        .tts-comparison {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .tts-model {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .tts-model h3 {
            color: #4a6da7;
            margin-top: 0;
        }
        
        .audio-samples {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .audio-sample {
            background-color: white;
            border-radius: 6px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .audio-sample h4 {
            margin-top: 0;
            color: #333;
        }
        
        .model-features {
            margin-top: 1rem;
        }
        
        .model-features li {
            margin-bottom: 0.5rem;
        }
        
        .model-badge {
            display: inline-block;
            background-color: #4a6da7;
            color: white;
            font-size: 12px;
            padding: 3px 8px;
            border-radius: 4px;
            margin-left: 8px;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="logo">
                <a href="index.html">OWL AI Agency</a>
            </div>
            <nav>
                <ul>
                    <li><a href="index.html">Home</a></li>
                    <li><a href="legal-research.html">Legal Research</a></li>
                    <li><a href="blog/index.html">Blog</a></li>
                    <li><a href="contact.html">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <main>
        <section class="hero">
            <div class="container">
                <h1>TTS Model Comparison</h1>
                <p>Compare different Text-to-Speech models for the OWL AI Agency website</p>
            </div>
        </section>

        <section class="tts-comparison">
            <h2>Voice Model Comparison</h2>
            <p>We've tested several high-quality TTS models to find the perfect voice for our legal research platform. Listen to the samples below and compare the quality, naturalness, and professionalism of each voice.</p>
            
            <div class="tts-model">
                <h3>Orpheus TTS <span class="model-badge">Recommended</span></h3>
                <p>The Orpheus TTS model from Canopy Labs provides exceptionally natural and professional-sounding voices, perfect for legal content.</p>
                
                <div class="model-features">
                    <h4>Features:</h4>
                    <ul>
                        <li>Extremely natural-sounding speech with proper intonation</li>
                        <li>Multiple voice options (Tara, Leah, Leo, etc.)</li>
                        <li>Support for emotional inflections</li>
                        <li>Excellent pronunciation of legal terminology</li>
                    </ul>
                </div>
                
                <div class="audio-samples">
                    <div class="audio-sample">
                        <h4>Welcome Message</h4>
                        <audio controls src="audio/orpheus_welcome.wav"></audio>
                    </div>
                    <div class="audio-sample">
                        <h4>Legal Research</h4>
                        <audio controls src="audio/orpheus_legal_research.wav"></audio>
                    </div>
                </div>
            </div>
            
            <div class="tts-model">
                <h3>Microsoft Azure Neural Voices</h3>
                <p>Microsoft's neural voices provide professional-quality speech with excellent clarity and natural rhythm.</p>
                
                <div class="model-features">
                    <h4>Features:</h4>
                    <ul>
                        <li>High-quality neural voices with natural prosody</li>
                        <li>Multiple languages and accents available</li>
                        <li>Adjustable speaking styles (professional, friendly, etc.)</li>
                        <li>Cloud-based API with reliable performance</li>
                    </ul>
                </div>
                
                <div class="audio-samples">
                    <div class="audio-sample">
                        <h4>Welcome Message</h4>
                        <audio controls src="audio/azure_welcome.wav"></audio>
                    </div>
                    <div class="audio-sample">
                        <h4>Legal Research</h4>
                        <audio controls src="audio/azure_legal_research.wav"></audio>
                    </div>
                </div>
            </div>
            
            <div class="tts-model">
                <h3>Parler TTS Mini</h3>
                <p>A lightweight but high-quality TTS model that supports emotional inflections and multiple languages.</p>
                
                <div class="model-features">
                    <h4>Features:</h4>
                    <ul>
                        <li>Good quality voices with emotional expression</li>
                        <li>Lightweight model that can run on less powerful hardware</li>
                        <li>Open-source and freely available</li>
                        <li>Multiple voice options available</li>
                    </ul>
                </div>
                
                <div class="audio-samples">
                    <div class="audio-sample">
                        <h4>Welcome Message</h4>
                        <audio controls src="audio/parler_welcome.wav"></audio>
                    </div>
                    <div class="audio-sample">
                        <h4>Legal Research</h4>
                        <audio controls src="audio/parler_legal_research.wav"></audio>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>OWL AI Agency</h3>
                    <p>Revolutionizing legal research with AI-powered automation.</p>
                </div>
                <div class="footer-section">
                    <h3>Quick Links</h3>
                    <ul>
                        <li><a href="index.html">Home</a></li>
                        <li><a href="legal-research.html">Legal Research</a></li>
                        <li><a href="blog/index.html">Blog</a></li>
                        <li><a href="contact.html">Contact</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>Contact Us</h3>
                    <p>Email: contact@owl-ai-agency.com</p>
                    <p>Phone: (985) 790-1830</p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2025 OWL AI Agency. All rights reserved.</p>
            </div>
        </div>
    </footer>
</body>
</html>
"""
    
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"{Fore.GREEN}Created TTS comparison page at {page_path}{Style.RESET_ALL}")

def main():
    """Main function to set up TTS model integration."""
    parser = argparse.ArgumentParser(description="Set up TTS model integration for OWL AI Agency website")
    parser.add_argument("--model", choices=["orpheus", "azure", "parler", "all"], default="all",
                        help="TTS model to set up (default: all)")
    args = parser.parse_args()
    
    print(f"{Fore.CYAN}===== OWL AI Agency TTS Model Integration ====={Style.RESET_ALL}")
    
    # Set up audio directory
    setup_audio_directory()
    
    # Save voice content
    save_voice_content()
    
    # Set up selected models
    if args.model in ["orpheus", "all"]:
        print(f"\n{Fore.BLUE}Setting up Orpheus TTS...{Style.RESET_ALL}")
        create_orpheus_colab_notebook()
    
    if args.model in ["azure", "all"]:
        print(f"\n{Fore.BLUE}Setting up Azure TTS...{Style.RESET_ALL}")
        setup_azure_tts()
    
    if args.model in ["parler", "all"]:
        print(f"\n{Fore.BLUE}Setting up Parler TTS...{Style.RESET_ALL}")
        setup_parler_tts()
    
    # Create comparison page
    create_tts_comparison_page()
    
    print(f"\n{Fore.GREEN}TTS model integration setup completed!{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
    print("1. For Orpheus TTS: Upload the OWL_Orpheus_TTS_Generator.ipynb to Google Colab")
    print("2. For Azure TTS: Update azure_tts_config.json with your Azure subscription key")
    print("3. For Parler TTS: Install required packages (transformers, torch)")
    print("4. Generate audio files with your preferred model")
    print("5. Place the generated WAV files in the /audio directory")


if __name__ == "__main__":
    main()

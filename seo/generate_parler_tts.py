#!/usr/bin/env python3
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
    """Generate speech using Parler TTS Mini."""
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
    """Generate all voice content using Parler TTS Mini."""
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

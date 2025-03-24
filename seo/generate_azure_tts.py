#!/usr/bin/env python3
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
    """Generate speech using Azure TTS."""
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
    """Generate all voice content using Azure TTS."""
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

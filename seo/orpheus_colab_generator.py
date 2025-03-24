#!/usr/bin/env python3
"""
Orpheus TTS Audio Generator for OWL AI Agency Website

This script creates a Google Colab notebook that will generate Orpheus TTS audio files
for the OWL AI Agency website. The notebook will guide you through the process of
generating high-quality voice clips using the Orpheus TTS model.
"""

import os
import json
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init()

# Configuration
WEBSITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_DIR = os.path.join(WEBSITE_ROOT, "audio")
COLAB_FILE = os.path.join(WEBSITE_ROOT, "seo", "OWL_Orpheus_TTS_Generator.ipynb")

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

def create_colab_notebook():
    """Create a Google Colab notebook for generating Orpheus TTS audio files."""
    
    # Create the notebook content
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Orpheus TTS Generator for OWL AI Agency\n",
                    "\n",
                    "This notebook will help you generate high-quality voice clips using the Orpheus TTS model from Canopy Labs.\n",
                    "\n",
                    "## Setup\n",
                    "\n",
                    "First, we need to install the required packages and set up the environment."
                ]
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Install required packages\n",
                    "!pip install orpheus-speech vllm==0.7.3 soundfile\n",
                    "!pip install -q huggingface_hub"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Authenticate with Hugging Face\n",
                    "\n",
                    "You'll need to authenticate with Hugging Face to access the Orpheus model. If you haven't already, request access to the model at [canopylabs/orpheus-tts-0.1-finetune-prod](https://huggingface.co/canopylabs/orpheus-tts-0.1-finetune-prod)."
                ]
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "from huggingface_hub import notebook_login\n",
                    "notebook_login()"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Import Orpheus and Set Up the Model\n",
                    "\n",
                    "Now we'll import the Orpheus TTS model and set it up for generating audio."
                ]
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "import torch\n",
                    "import soundfile as sf\n",
                    "from orpheus import OrpheusTTS\n",
                    "\n",
                    "# Check if CUDA is available\n",
                    "print(f\"CUDA available: {torch.cuda.is_available()}\")\n",
                    "if torch.cuda.is_available():\n",
                    "    print(f\"CUDA device: {torch.cuda.get_device_name(0)}\")\n",
                    "\n",
                    "# Initialize the Orpheus TTS model\n",
                    "model = OrpheusTTS()\n",
                    "print(\"Model loaded successfully!\")"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Generate Audio Files\n",
                    "\n",
                    "Now we'll generate audio files for each of the voice content pieces for the OWL AI Agency website."
                ]
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Create a directory to store the generated audio files\n",
                    "!mkdir -p audio_files"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Voice content configuration\n",
                    "voice_content = " + json.dumps(VOICE_CONTENT, indent=4)
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# FAQ data for voice responses\n",
                    "faq_data = " + json.dumps(FAQ_DATA, indent=4)
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Function to generate audio files\n",
                    "def generate_audio(text, output_path, voice=\"tara\"):\n",
                    "    print(f\"Generating audio for: {text[:50]}...\")\n",
                    "    output = model.inference(text, voice=voice)\n",
                    "    audio = output.cpu().numpy().squeeze()\n",
                    "    sf.write(output_path, audio, 24000)\n",
                    "    print(f\"Audio saved to {output_path}\")\n",
                    "    return output_path\n",
                    "\n",
                    "# Select voice to use\n",
                    "selected_voice = \"tara\"  # Options: tara, leah, jess, leo, dan, mia, zac, zoe\n",
                    "\n",
                    "# Generate audio for main content\n",
                    "for key, text in voice_content.items():\n",
                    "    output_path = f\"audio_files/{key}.wav\"\n",
                    "    generate_audio(text, output_path, voice=selected_voice)\n",
                    "\n",
                    "# Generate audio for FAQs\n",
                    "for i, faq in enumerate(faq_data):\n",
                    "    output_path = f\"audio_files/faq_{i}.wav\"\n",
                    "    generate_audio(faq[\"answer\"], output_path, voice=selected_voice)"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Play Audio Files\n",
                    "\n",
                    "Let's listen to the generated audio files to make sure they sound good."
                ]
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "from IPython.display import Audio, display\n",
                    "\n",
                    "# Play the welcome message\n",
                    "print(\"Welcome message:\")\n",
                    "display(Audio(\"audio_files/welcome.wav\"))\n",
                    "\n",
                    "# Play the legal research message\n",
                    "print(\"Legal research message:\")\n",
                    "display(Audio(\"audio_files/legal_research.wav\"))"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Download Audio Files\n",
                    "\n",
                    "Now let's create a zip file with all the generated audio files so you can download them and add them to your website."
                ]
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Create a zip file with all the audio files\n",
                    "!zip -r audio_files.zip audio_files\n",
                    "\n",
                    "# Download the zip file\n",
                    "from google.colab import files\n",
                    "files.download('audio_files.zip')"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Next Steps\n",
                    "\n",
                    "1. Extract the downloaded zip file\n",
                    "2. Copy the WAV files to the `/audio` directory in your OWL AI Agency website\n",
                    "3. The voice player will automatically use these files instead of the browser's speech synthesis\n",
                    "\n",
                    "Congratulations! You've successfully generated high-quality voice clips using the Orpheus TTS model."
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.7.12"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    # Write the notebook to a file
    try:
        with open(COLAB_FILE, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        print(f"{Fore.GREEN}Created Orpheus TTS Generator notebook at {COLAB_FILE}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Error creating Orpheus TTS Generator notebook: {str(e)}{Style.RESET_ALL}")
        return False

def create_instructions():
    """Create instructions for using the Colab notebook."""
    instructions_file = os.path.join(WEBSITE_ROOT, "seo", "ORPHEUS_COLAB_INSTRUCTIONS.md")
    
    instructions = f"""# Orpheus TTS Generator Instructions

## Overview

This document provides instructions for generating high-quality voice clips using the Orpheus TTS model from Canopy Labs via Google Colab.

## Prerequisites

1. A Google account to access Google Colab
2. A Hugging Face account with access to the Orpheus model

## Step 1: Request Access to the Orpheus Model

1. Go to [canopylabs/orpheus-tts-0.1-finetune-prod](https://huggingface.co/canopylabs/orpheus-tts-0.1-finetune-prod)
2. Click "Access repository" and fill out the access request form
3. Wait for approval (usually within 24 hours)

## Step 2: Upload and Run the Colab Notebook

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click on "File" > "Upload notebook"
3. Upload the `OWL_Orpheus_TTS_Generator.ipynb` file from this directory
4. Run each cell in the notebook by clicking the play button next to each cell or by pressing Shift+Enter

## Step 3: Authenticate with Hugging Face

When prompted, enter your Hugging Face token:
1. Go to [Hugging Face tokens](https://huggingface.co/settings/tokens)
2. Create a new token if you don't have one
3. Copy the token and paste it into the Colab notebook when prompted

## Step 4: Generate and Download Audio Files

1. The notebook will generate audio files for all the voice content
2. At the end, it will create a zip file and prompt you to download it
3. Download the zip file to your computer

## Step 5: Add Audio Files to Your Website

1. Extract the downloaded zip file
2. Copy all the WAV files to the `/audio` directory in your OWL AI Agency website
3. The voice player will automatically use these files instead of the browser's speech synthesis

## Voice Options

If you want to change the voice used, modify the `selected_voice` variable in the notebook:
- tara (default) - Most natural female voice
- leah - Female voice
- jess - Female voice
- leo - Male voice
- dan - Male voice
- mia - Female voice
- zac - Male voice
- zoe - Female voice

## Troubleshooting

If you encounter any issues:
1. Make sure you have been granted access to the Orpheus model on Hugging Face
2. Check that you're using a valid Hugging Face token
3. Ensure you're running the notebook with GPU acceleration enabled (Runtime > Change runtime type > GPU)

## Resources

- [Orpheus GitHub Repository](https://github.com/canopyai/Orpheus-TTS)
- [Orpheus Blog Post](https://canopylabs.ai/model-releases)
- [Hugging Face Model](https://huggingface.co/canopylabs/orpheus-tts-0.1-finetune-prod)
"""
    
    try:
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print(f"{Fore.GREEN}Created Orpheus Colab instructions at {instructions_file}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Error creating Orpheus Colab instructions: {str(e)}{Style.RESET_ALL}")
        return False

def main():
    """Main function to create the Orpheus TTS Generator notebook."""
    print(f"{Fore.CYAN}===== Creating Orpheus TTS Generator Notebook ====={Style.RESET_ALL}")
    
    # Create the Colab notebook
    create_colab_notebook()
    
    # Create instructions for using the notebook
    create_instructions()
    
    print(f"\n{Fore.GREEN}Orpheus TTS Generator notebook created successfully!{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
    print("1. Follow the instructions in ORPHEUS_COLAB_INSTRUCTIONS.md")
    print("2. Upload the OWL_Orpheus_TTS_Generator.ipynb to Google Colab")
    print("3. Run the notebook to generate the audio files")
    print("4. Download the generated audio files and add them to your website")


if __name__ == "__main__":
    main()

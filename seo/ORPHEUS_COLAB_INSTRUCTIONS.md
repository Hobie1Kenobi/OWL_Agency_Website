# Orpheus TTS Generator Instructions

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

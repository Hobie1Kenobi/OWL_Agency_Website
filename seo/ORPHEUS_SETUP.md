# Orpheus TTS Integration for OWL AI Agency

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

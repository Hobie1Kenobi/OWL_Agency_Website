---
library_name: transformers
language:
- en
pipeline_tag: text-to-speech
license: apache-2.0
base_model:
- meta-llama/Llama-3.2-3B-Instruct
- canopylabs/orpheus-3b-0.1-pretrained
---

# Orpheus 3B 0.1 Finetuned

**03/18/2025** – We are releasing our 3B Orpheus TTS model with additional finetunes. Code is available on GitHub: [CanopyAI/Orpheus-TTS](https://github.com/canopyai/Orpheus-TTS)

---

Orpheus TTS is a state-of-the-art, Llama-based Speech-LLM designed for high-quality, empathetic text-to-speech generation. This model has been finetuned to deliver human-level speech synthesis, achieving exceptional clarity, expressiveness, and real-time streaming performances.

# Model Details

### Model Capabilities

- **Human-Like Speech**: Natural intonation, emotion, and rhythm that is superior to SOTA closed source models
- **Zero-Shot Voice Cloning**: Clone voices without prior fine-tuning
- **Guided Emotion and Intonation**: Control speech and emotion characteristics with simple tags
- **Low Latency**: ~200ms streaming latency for realtime applications, reducible to ~100ms with input streaming


### Model Sources

- **GitHub Repo:** [https://github.com/canopyai/Orpheus-TTS](https://github.com/canopyai/Orpheus-TTS)
- **Blog Post:** [https://canopylabs.ai/model-releases](https://canopylabs.ai/model-releases)
- **Colab Inference Notebook:** [notebook link](https://colab.research.google.com/drive/1KhXT56UePPUHhqitJNUxq63k-pQomz3N?usp=sharing)


# Usage

Check out our Colab ([link to Colab](https://colab.research.google.com/drive/1KhXT56UePPUHhqitJNUxq63k-pQomz3N?usp=sharing)) or GitHub ([link to GitHub](https://github.com/canopyai/Orpheus-TTS)) on how to run easy inference on our finetuned models.


# Model Misuse
Do not use our models for impersonation without consent, misinformation or deception (including fake news or fraudulent calls), or any illegal or harmful activity. By using this model, you agree to follow all applicable laws and ethical guidelines. We disclaim responsibility for any use.
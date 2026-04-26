# Gemma4-AMD-Success

gemma-4-26b AMD 6750XT 12GB export

This folder is a curated code/batch export for Git upload.

Included:
- 26B GGUF IQ3/IQ2 launchers
- InternVL3-8B GGUF (Q4_K_M + mmproj) launcher
- chat launcher helpers
- llama_gguf runtime config/start scripts
- control/help and 26B operation guides

Not included:
- model weights (`*.gguf`, `*.safetensors`)
- virtualenv (`.venv`)
- runtime logs/tmp

Model path on target machine:
- Recommended: `<repo_root>\Model\gemma-4-26B-A4B-it-GGUF`
- Or set env: `VT_MODEL_BASE=<your_model_root>`

Model file not included / License compliant.

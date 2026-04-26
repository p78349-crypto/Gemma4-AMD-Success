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

-------------------------------------------------------------
<img width="1358" height="1546" alt="image" src="https://github.com/user-attachments/assets/d0ce3692-56e2-4dc8-8bfb-7833b664da53" />

포함:
- 26B GGUF IQ3/IQ2 실행 배치
- InternVL3-8B GGUF (Q4_K_M + mmproj) 실행 배치
- 채팅 실행 보조 배치
- llama_gguf 실행 설정/스크립트
- 

미포함:
- 모델 가중치 (`*.gguf`, `*.safetensors`)
- 가상환경 (`.venv`)
- 런타임 로그/tmp

대상 PC 모델 경로:
- 권장: `<repo_root>\Model\gemma-4-26B-A4B-it-GGUF`
- 또는 환경변수: `VT_MODEL_BASE=<your_model_root>`

모델 파일 미포함 / 라이선스 준수.
<img width="1382" height="1525" alt="image" src="https://github.com/user-attachments/assets/e8b67308-1dd8-48b6-83ba-5c42d526a91b" />
-----------------------------------------------------------------
## Gemma4 E4B Q8 실행 성공

### 실행 환경
- GPU: AMD Radeon 6750XT (12GB VRAM)
- 런타임: Vulkan 기반 llama.cpp
- 모델: Gemma4 E4B Q8 GGUF

### 성과
- AMD GPU에서 Q8 양자화 모델을 안정적으로 구동 성공
- 긴 문서 입력(OCR 텍스트 포함) 처리 가능
- 출력 결과가 자연스럽고, 교정/번역 작업에 활용 가능

### 비교 (vs Gemma4 26B)
- **26B**: 최고 성능, 긴 문맥 처리와 추론력이 뛰어나 초벌 번역가로 적합
- **E4B Q8**: 상대적으로 가볍고 빠르며, GPU 메모리 부담이 적음 → 테스트 및 경량 작업에 유용
- 결론: 26B는 “최고 성능”, E4B Q8은 “실용적 경량 모델”로 병행 활용 가능

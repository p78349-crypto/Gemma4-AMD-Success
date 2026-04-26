# Gemma4-AMD-Success

gemma-4-26b AMD 6750XT 12GB 공개용 내보내기

이 폴더는 Git 업로드를 위한 코드/배치 추출본입니다.

포함:
- 26B GGUF IQ3/IQ2 실행 배치
- InternVL3-8B GGUF (Q4_K_M + mmproj) 실행 배치
- 채팅 실행 보조 배치
- llama_gguf 실행 설정/스크립트
- 도움말/26B 운용 가이드

미포함:
- 모델 가중치 (`*.gguf`, `*.safetensors`)
- 가상환경 (`.venv`)
- 런타임 로그/tmp

대상 PC 모델 경로:
- 권장: `<repo_root>\Model\gemma-4-26B-A4B-it-GGUF`
- 또는 환경변수: `VT_MODEL_BASE=<your_model_root>`

모델 파일 미포함 / 라이선스 준수.

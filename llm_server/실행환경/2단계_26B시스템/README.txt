========================================================
  2단계 — 26B 시스템 환경 (AMD GPU Vulkan 풀 파이프라인)
========================================================

[ 지원 모델 ]
  - Gemma4-26B GGUF  (번역/LLM)  포트 8031  VRAM ~10.4GB
  - NLLB-1.3B        (전문번역)   포트 8012  RAM  ~2.7GB
  - Whisper Turbo    (STT)        포트 8021  RAM  ~1.5GB

[ GPU 요구 사양 ]
  - AMD GPU VRAM 12GB+ (예: RX 6750 XT) — Vulkan 사용
  - IQ3_S(10.4GB) → 12GB VRAM에 전체 레이어 올라감
  - VRAM 부족 시: IQ2_M(9.3GB) 또는 IQ2_XXS(9.2GB) 선택

[ GGUF 파일 위치 ]
  <프로젝트루트>\Model\
  gemma-4-26B-A4B-it-GGUF\
    - gemma-4-26B-A4B-it-UD-IQ3_S.gguf    (10.4GB 최고품질)
    - gemma-4-26B-A4B-it-UD-IQ2_M.gguf    ( 9.3GB 절약)
    - gemma-4-26B-A4B-it-UD-IQ2_XXS.gguf  ( 9.2GB 초절약)

[ 실행 방법 ]
  방법1: 실행.bat       — 서버시작 + 데모 자동 실행
  방법2: 서버시작.bat   — 서버만 백그라운드 시작
         이후 데모테스트.bat 별도 실행 가능
  방법3: 서버시작_IQ2M.bat — VRAM 절약 버전 (IQ2_M)
  방법4: 서버시작_선택형.bat — 1차모델/2차교정/STT 선택 기동

[ 포트 구성 ]
  26B GGUF   : http://localhost:8031/v1/chat/completions
  NLLB-1.3B  : http://localhost:8012/v1/translate
  Whisper    : http://localhost:8021/v1/transcribe

[ 26B vs NLLB 역할 분담 ]
  - 26B: 문맥 이해 번역, 교정, 요약, 자유 대화
  - NLLB: 빠른 직역, SRT 자막 대량 번역 (속도 우선)
  자세한 내용: 26B활용_가이드.txt 참조

[ 전제 조건 ]
  - llm_server\.venv\ 가상환경 설치 완료
  - llama_gguf\bin\llama-server.exe 존재 확인
  - GGUF 파일 다운로드 완료

[ start_26b_iq3 버전 정보 (기준일: 2026-04-26) ]
  - 실행 배치: exebat\start_26b_iq3.bat
  - 실행 인자: --family 26b --model IQ3_S --port 8031 --ngl 99
  - Python: 3.12.10
  - llama-server.exe: version 8808 (408225bb1)
  - llama-server build: Clang 19.1.5 (Windows x86_64)
  - GGUF 모델 파일: gemma-4-26B-A4B-it-UD-IQ3_S.gguf
  - GGUF 포맷: version 3 (magic: GGUF)
  - 백엔드 DLL: ggml-vulkan.dll, ggml-cpu-zen4.dll, ggml-rpc.dll

========================================================

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
<img width="1358" height="1546" alt="image" src="https://github.com/user-attachments/assets/d0ce3692-56e2-4dc8-8bfb-7833b664da53" />

모델 파일 미포함 / 라이선스 준수.
----------------------------------------------------------------

InternVL3-8B 실행 성공
![InternVL3-8B 실행 성공 스크린샷](./images/internvl3.png)

- 이미지+텍스트 멀티모달 입력 처리 가능
- OCR 이미지 캡션, 시각 자료 분석에 적합
- 텍스트 단독 성능은 Gemma4-26B 대비 낮음
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
<img width="1358" height="1551" alt="image" src="https://github.com/user-attachments/assets/1186d258-3b7f-4e84-a74d-aa05ff292a6b" />
--------------------------------------------------------------------------
## 모델 성능 비교 (한글)

| 모델명        | 강점                  | 활용 분야                  | 제한점 |
|---------------|-----------------------|----------------------------|--------|
| Gemma4-26B    | 긴 문맥 처리, 추론력 우수 | OCR 교정, 초벌 번역, 요약 | VRAM 부담 큼 |
| Gemma4-E4B Q8 | 가볍고 빠름, 메모리 효율적 | 테스트, 경량 작업          | 성능은 26B 대비 낮음 |
| InternVL3-8B  | 이미지+텍스트 멀티모달 처리 | OCR 이미지 캡션, 시각 자료 | 텍스트 단독 성능 약함 |

---

## Model Performance Comparison (English)

| Model         | Strengths                  | Use Cases                  | Limitations |
|---------------|----------------------------|----------------------------|-------------|
| Gemma4-26B    | Strong long-context reasoning | OCR correction, draft translation, summarization | High VRAM usage |
| Gemma4-E4B Q8 | Lightweight, memory efficient | Testing, lightweight tasks | Lower performance vs 26B |
| InternVL3-8B  | Handles image+text multimodal | OCR image captioning, visual-text analysis | Weaker text-only performance |


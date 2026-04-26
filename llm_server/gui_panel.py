"""
모델 서버 + EPUB 번역 GUI 제어판 (tkinter)

  탭1: 서버 제어  — 1단계/2단계 시작·종료
  탭2: 모델 개별실행 — 모든 모델 단독 시작/종료
  탭3: EPUB 번역  — 3폼 (언어/1차모델/2차교정)
"""
import os
import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from gui_tabs.server_tab import ServerTab
from gui_tabs.model_tab import ModelTab
from gui_tabs.epub_tab import EpubTab
from gui_tabs.chat_tab import ChatTab
from gui_tabs.convert_tab import ConvertTab

_ROOT = Path(__file__).resolve().parent
_PY   = _ROOT / ".venv" / "Scripts" / "python.exe"


def _ensure_tk_env() -> None:
    """Windows venv 에서 Tcl/Tk 경로를 못 찾는 경우를 보정."""
    base_prefix = Path(getattr(sys, "base_prefix", sys.prefix))
    tcl_root = base_prefix / "tcl"
    tcl_dir = tcl_root / "tcl8.6"
    tk_dir = tcl_root / "tk8.6"
    if tcl_dir.exists():
        os.environ.setdefault("TCL_LIBRARY", str(tcl_dir))
    if tk_dir.exists():
        os.environ.setdefault("TK_LIBRARY", str(tk_dir))


_ensure_tk_env()

C_BG    = "#F5F5F5"
C_TEXT  = "#212121"
C_SUB   = "#757575"
C_PANEL = "#FFFFFF"

HELP_TEXT = r"""\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 탭 안내
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  서버 제어       단계별 일괄 시작/종료 (1단계 8GB · 2단계 26B)
  모델 개별실행   모든 모델 하나씩 단독 시작/종료
  파일 번역       EPUB · SRT · TXT · DOCX 번역 실행
  GGUF 변환       HuggingFace safetensors → GGUF 변환 + 양자화
                  (E4B/E2B 모델, F16/Q8_0/Q5_K_M/Q4_K_M/Q3_K_M)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 번역 모델 (NLLB)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NLLB-600M         포트 8011   빠름 · RAM 2GB
  NLLB-1.3B         포트 8012   균형
  NLLB-3.3B         포트 8013   고품질 · RAM 7GB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 LLM / 교정 모델 (Gemma — HuggingFace)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Gemma4-E2B        포트 8001   교정 전용 · VRAM 4GB
  Gemma4-E4B        포트 8002   고품질 교정 · VRAM 8GB (비전 지원)
  Gemma4-26B        포트 8003   배치 전용 · 단독 운용
  InternVL2.5-4B    포트 8004   비전 전용 · 이미지 분석

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 LLM (GGUF — llama.cpp / Vulkan GPU)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Gemma4-E2B F16    포트 8032   VRAM ~4GB (전체 정밀도)
  Gemma4-26B IQ3_S  포트 8031   VRAM ~10.4GB
  Gemma4-26B IQ2_M  포트 8031   VRAM ~9.3GB (절약)
  ※ IQ3_S / IQ2_M 동시 실행 불가 (포트 공유)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 STT — 음성 인식 (Whisper)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Whisper Turbo     포트 8021   빠름 · 권장
  Whisper Large     포트 8022   고품질  ※ TTS와 포트 충돌
  Whisper Large FP32 포트 8023  정확도 최대 · RAM 최대

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 TTS — 음성 합성
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TTS Edge          포트 8022   ※ Whisper Large와 포트 충돌

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 웹 접속 방법 (브라우저 / HTTP)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  상태 확인 (health check)
    http://localhost:8011/health     NLLB-600M
    http://localhost:8012/health     NLLB-1.3B
    http://localhost:8013/health     NLLB-3.3B
    http://localhost:8001/health     Gemma4-E2B (HF)
    http://localhost:8002/health     Gemma4-E4B (HF · 비전)
    http://localhost:8003/health     Gemma4-26B (HF)
    http://localhost:8004/health     InternVL2.5-4B (HF · 비전)
    http://localhost:8032/health     Gemma4-E2B GGUF F16
    http://localhost:8031/health     26B GGUF (IQ3_S / IQ2_M)
    http://localhost:8021/health     Whisper Turbo
    http://localhost:8022/health     Whisper Large / TTS Edge
    http://localhost:8023/health     Whisper Large FP32

  모델 목록 확인
    http://localhost:<포트>/v1/models

  번역 API  (NLLB 계열)
    POST http://localhost:8011/v1/translate
    POST http://localhost:8012/v1/translate
    POST http://localhost:8013/v1/translate

  LLM 채팅 API  (Gemma / GGUF)
    POST http://localhost:8001/v1/chat/completions  (E2B HF)
    POST http://localhost:8002/v1/chat/completions  (E4B HF · 비전)
    POST http://localhost:8003/v1/chat/completions  (26B HF)
    POST http://localhost:8004/v1/chat/completions  (InternVL2.5-4B · 비전)
    POST http://localhost:8032/v1/chat/completions  (E2B GGUF)
    POST http://localhost:8031/v1/chat/completions  (26B GGUF)

  STT 음성 인식  (Whisper)
    POST http://localhost:8021/v1/transcribe
    POST http://localhost:8022/v1/transcribe
    POST http://localhost:8023/v1/transcribe

  TTS 음성 합성
    POST http://localhost:8022/v1/synthesize

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 브라우저 주소창 한계 & 대화 방법
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  주소창에 http://localhost:8031/health 입력
  → 서버 상태 확인만 가능 (GET 요청)
  → LLM 대화 불가 (대화는 POST 요청 필요)

  ■ curl 로 대화 (터미널)
    curl http://localhost:8031/v1/chat/completions ^
      -H "Content-Type: application/json" ^
      -d "{\"model\":\"gemma\",\"messages\":[{\"role\":\"user\",\"content\":\"안녕\"}]}"

  ■ Open WebUI (브라우저에서 ChatGPT처럼 대화)
    1) pip install open-webui
    2) open-webui serve
    3) http://localhost:8080 접속
    4) 설정 → 연결 → http://localhost:8031 추가
    → GGUF / Gemma 모델 모두 연결 가능

  ■ Python 코드로 호출
    import requests
    r = requests.post(
        "http://localhost:8031/v1/chat/completions",
        json={"model":"gemma",
              "messages":[{"role":"user","content":"안녕"}]}
    )
    print(r.json())

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 VS Code 에서 로컬 서버 모델 사용
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ■ Continue 확장 (코드 보조 / 채팅)
   VS Code 확장: "Continue" 검색 후 설치
   설정 파일: C:\Users\<이름>\.continue\config.json

   {
     "models": [
       {
         "title": "Gemma4-26B (Local GGUF)",
         "provider": "openai",
         "model": "gemma",
         "apiBase": "http://localhost:8031",
         "apiKey": "local"
       },
       {
         "title": "Gemma4-E2B (Local GGUF)",
         "provider": "openai",
         "model": "gemma",
         "apiBase": "http://localhost:8032",
         "apiKey": "local"
       },
       {
         "title": "Gemma4-E4B (Local HF)",
         "provider": "openai",
         "model": "gemma4-e4b",
         "apiBase": "http://localhost:8002",
         "apiKey": "local"
       },
       {
         "title": "InternVL2.5-4B (Local Vision)",
         "provider": "openai",
         "model": "internvl2.5-4b",
         "apiBase": "http://localhost:8004",
         "apiKey": "local"
       }
     ]
   }

   사용법:
     Ctrl+L  → 채팅 패널 (질문/코드 설명)
     Ctrl+I  → 인라인 코드 편집
     선택 후 Ctrl+L  → 선택 코드 분석

 ────────────────────────────────────────────────
 ■ Cline 확장 (자율 코딩 에이전트)
   VS Code 확장: "Cline" 검색 후 설치
   설정: API Provider → OpenAI Compatible
     Base URL : http://localhost:8031
     API Key  : local  (임의 문자열)
     Model ID : gemma

 ────────────────────────────────────────────────
 ■ CodeGPT 확장
   VS Code 확장: "CodeGPT" 검색 후 설치
   설정: AI Provider → OpenAI 호환
     API URL  : http://localhost:8031/v1
     API Key  : local

 ────────────────────────────────────────────────
 ■ 공통 API 접속 정보 (모든 확장 공통)
   Base URL  : http://localhost:<포트>/v1
   API Key   : local  (값 무관, 인증 없음)
   Model ID  : 아무 문자열  (서버가 무시)

   포트 선택 기준:
     8031  Gemma4-26B GGUF  → 복잡한 코드/설계 질문
     8032  Gemma4-E2B GGUF  → 빠른 응답, 단순 질문
     8001  Gemma4-E2B HF    → CPU 폴백
     8002  Gemma4-E4B HF    → 비전(이미지) 포함 질문
     8004  InternVL2.5-4B   → 문서/OCR/이미지 분석

 ────────────────────────────────────────────────
 ■ 확장 없이 직접 호출 (Python / 터미널)
   import openai
   client = openai.OpenAI(
       base_url="http://localhost:8031/v1",
       api_key="local",
   )
   r = client.chat.completions.create(
       model="gemma",
       messages=[{"role":"user","content":"코드 설명해줘"}],
   )
   print(r.choices[0].message.content)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 로컬 모델 추가 방법
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ■ GGUF 모델 추가 (llama.cpp / Vulkan GPU)
   → 기존 Gemma4 계열과 동일 아키텍처 권장

   1) .gguf 파일을 Model 폴더에 배치

   2) llm_server\llama_gguf\start.py 편집
      _FAMILY_MAP 에 새 패밀리 추가:
        "신모델": {
            "dir": Path("Model 경로"),
            "default_model": "Q4_K_M",
            "default_port":  8033,
            "models": { "Q4_K_M": "파일명.gguf" },
        },

   3) llm_server\gui_tabs\model_tab.py 편집
      MODELS["LLM (GGUF — llama.cpp)"] 목록에 추가:
        ("키", "표시명", 포트, C_GGUF,
         f'"{_PY}" llama_gguf\\start.py --family 신모델 --port 8033 --ngl 99',
         "표시명 :8033", "VRAM 예상"),

   4) (선택) gui_tabs\chat_tab.py 편집
      LLM_SERVERS 에 추가:
        ("[07]  표시명  :8033", 8033),

   ※ safetensors → GGUF 변환: [GGUF 변환] 탭 사용

 ────────────────────────────────────────────────
 ■ HuggingFace 모델 추가 (transformers / Python)

   1) 모델 폴더를 Model 경로에 배치
      예) C:\\...\\Model\\NewModel-7B\\

   2) llm_server\shared\config.py 편집
      MODEL_PATHS["new-7b"] = _BASE / "NewModel-7B"
      SERVER_PORTS["new-7b"] = 8004   ← 미사용 포트

   3) 기존 server.py 복사해서 신규 폴더 생성
      llm_server\newmodel_7b\server.py
      → MODEL_ID, 포트, 모델 클래스(Causal/VisionText) 수정

   4) gui_tabs\model_tab.py 편집
      MODELS["LLM (Gemma — HuggingFace)"] 에 추가:
        ("키", "표시명", 8004, C_GEMMA,
         f'"{_PY}" -m uvicorn newmodel_7b.server:app --port 8004 --workers 1',
         "표시명 :8004", ""),

   5) (선택) gui_tabs\chat_tab.py 편집
      LLM_SERVERS 에 추가:
        ("[07]  표시명  :8004", 8004),

 ────────────────────────────────────────────────
 ■ 포트 배정 현황 (추가 시 참고)
   8001~8003  Gemma HF       8031~8032  GGUF
   8011~8013  NLLB 번역      8033~      미사용 (신규 할당)
   8021~8023  Whisper STT
   8022       TTS Edge (Whisper Large와 공유)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 기본 사용법
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1) [서버 제어] → 단계 선택하여 일괄 시작
     또는 [모델 개별실행] → 원하는 모델만 시작
  2) 상태 표시 ● 녹색 = 실행 중 / 회색 = 미실행
  3) [파일 번역] → 파일 선택 → 언어 선택 → 번역 실행
  4) 종료: 각 모델 [종료] 버튼 또는 [전체 종료]
"""


class ControlPanel(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("모델 서버 제어판")
        self.resizable(False, False)
        self.configure(bg=C_BG)
        self._build_ui()

    def _build_ui(self) -> None:
        # 상단 헤더 (제목 + 도움말 버튼)
        header = tk.Frame(self, bg=C_BG)
        header.pack(fill="x", padx=14, pady=(12, 4))

        tk.Label(
            header, text="모델 서버 제어판",
            font=("맑은 고딕", 13, "bold"),
            bg=C_BG, fg=C_TEXT,
        ).pack(side="left")

        tk.Button(
            header, text="? 도움말",
            font=("맑은 고딕", 9),
            bg="#E0E0E0", fg=C_TEXT,
            activebackground="#BDBDBD",
            relief="flat", bd=0, cursor="hand2",
            padx=10, pady=3,
            command=self._show_help,
        ).pack(side="right")

        style = ttk.Style()
        style.configure("TNotebook", background=C_BG)
        style.configure("TNotebook.Tab", font=("맑은 고딕", 10), padding=[14, 6])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        server_tab  = ServerTab(nb)
        model_tab   = ModelTab(nb)
        epub_tab    = EpubTab(nb)
        chat_tab    = ChatTab(nb)
        convert_tab = ConvertTab(nb)

        nb.add(server_tab,  text="  서버 제어  ")
        nb.add(model_tab,   text="  모델 개별실행  ")
        nb.add(epub_tab,    text="  파일 번역  ")
        nb.add(chat_tab,    text="  LLM 채팅  ")
        nb.add(convert_tab, text="  GGUF 변환  ")

        # 실행 옵션: VT_GUI_OPEN_TAB=chat 면 채팅 탭을 기본으로 연다.
        if os.environ.get("VT_GUI_OPEN_TAB", "").strip().lower() == "chat":
            nb.select(chat_tab)

    def _show_help(self) -> None:
        win = tk.Toplevel(self)
        win.title("도움말 — 모델 & 포트 정보")
        win.configure(bg=C_BG)
        win.resizable(False, False)
        win.grab_set()

        txt = tk.Text(
            win,
            font=("맑은 고딕", 9),
            bg=C_PANEL, fg=C_TEXT,
            relief="flat", bd=0,
            padx=16, pady=12,
            width=56, height=100,
            wrap="none",
            state="normal",
        )
        txt.insert("1.0", HELP_TEXT)
        txt.configure(state="disabled")
        txt.pack(padx=10, pady=(10, 4))

        tk.Button(
            win, text="닫기",
            font=("맑은 고딕", 10),
            bg="#E0E0E0", fg=C_TEXT,
            activebackground="#BDBDBD",
            relief="flat", bd=0, cursor="hand2",
            padx=20, pady=5,
            command=win.destroy,
        ).pack(pady=(0, 12))


if __name__ == "__main__":
    if not _PY.exists():
        print(
            "[오류] 가상환경 없음.\n"
            "llm_server\\00_setup.bat 먼저 실행하세요.",
            file=sys.stderr,
        )
        sys.exit(1)
    app = ControlPanel()
    app.mainloop()


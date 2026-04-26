"""llm_server 중앙 설정."""
import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LOCAL_BASE = _REPO_ROOT / "Model"
_FALLBACK_BASE_RAW = os.environ.get("VT_MODEL_BASE_FALLBACK", "").strip()
_FALLBACK_BASE = Path(_FALLBACK_BASE_RAW) if _FALLBACK_BASE_RAW else _LOCAL_BASE
_ENV_BASE_RAW = os.environ.get("VT_MODEL_BASE", "").strip()
_ENV_BASE = Path(_ENV_BASE_RAW) if _ENV_BASE_RAW else None


def _model_dir(*parts: str) -> Path:
    """ENV(VT_MODEL_BASE) -> 저장소 Model -> ENV(VT_MODEL_BASE_FALLBACK) 순서."""
    if _ENV_BASE:
        env_path = _ENV_BASE.joinpath(*parts)
        if env_path.exists():
            return env_path
    local = _LOCAL_BASE.joinpath(*parts)
    if local.exists():
        return local
    return _FALLBACK_BASE.joinpath(*parts)


if _ENV_BASE and _ENV_BASE.exists():
    _BASE = _ENV_BASE
elif _LOCAL_BASE.exists():
    _BASE = _LOCAL_BASE
else:
    _BASE = _FALLBACK_BASE

# 26b: AutoRound INT4 폴더에 index 파일 없음
# → 원본 폴더(BF16) 사용 + optimum-quanto INT4 런타임 적용
_26B_PATH = _model_dir("Gemma-4-26B-A4B-it")
_26B_TOK_PATH = _26B_PATH  # 동일 폴더

MODEL_PATHS: dict[str, Path] = {
    "gemma4-e2b": _model_dir("gemma-4-E2B-it"),
    "gemma4-e4b": _model_dir("gemma-4-E4B-it"),
    "gemma4-26b": _26B_PATH,
    "internvl2.5-4b": _model_dir("InternVL2.5-4 4B"),
}
# 토크나이저 경로 별도 관리 (가중치 경로와 다를 수 있음)
TOKENIZER_PATHS: dict[str, Path] = {
    "gemma4-e2b": _model_dir("gemma-4-E2B-it"),
    "gemma4-e4b": _model_dir("gemma-4-E4B-it"),
    "gemma4-26b": _26B_TOK_PATH,  # AutoRound엔 토크나이저 없음
    "internvl2.5-4b": _model_dir("InternVL2.5-4 4B"),
}

# True: 모델이 사전 양자화됨 → QuantoConfig 재적용 금지
PRE_QUANTIZED: dict[str, bool] = {
    "gemma4-e2b": False,
    "gemma4-e4b": False,
    "gemma4-26b": False,  # 원본 BF16 사용 + quanto INT4 런타임 적용
    "internvl2.5-4b": False,
}

SERVER_PORTS: dict[str, int] = {
    "gemma4-e2b": 8001,
    "gemma4-e4b": 8002,
    "gemma4-26b": 8003,
    "internvl2.5-4b": 8004,
}

# ── NLLB-200 (전문 번역 seq2seq) ─────────────────────
NLLB_PATHS: dict[str, Path] = {
    "nllb-600m": _model_dir("nllb-200-distilled-600M"),
    "nllb-1p3b": _model_dir("nllb-200-1.3B"),
    "nllb-3p3b": _model_dir("nllb-200-3.3B"),  # 다운로드 필요
}

NLLB_PORTS: dict[str, int] = {
    "nllb-600m": 8011,
    "nllb-1p3b": 8012,
    "nllb-3p3b": 8013,
}

# ── Whisper STT (faster-whisper / whisperX) ───────────
_W = _BASE
WHISPER_PATHS: dict[str, Path] = {
    "whisper-turbo":   _model_dir("faster-whisper-large-v3-turbo"),
    "whisper-large":   _model_dir("faster-whisper-large-v3"),
    "whisper-large-fp32": _model_dir("faster-whisper-large-v3-fp32"),
}
WHISPER_PORTS: dict[str, int] = {
    "whisper-turbo":      8021,
    "whisper-large":      8022,
    "whisper-large-fp32": 8023,
}
# CTranslate2 compute_type per model
WHISPER_COMPUTE: dict[str, str] = {
    "whisper-turbo":      "int8",
    "whisper-large":      "int8",
    "whisper-large-fp32": "float32",
}
WHISPERX_PATH = _model_dir("whisperX-main")

# ── GGUF / llama.cpp (SSD mmap 지연 로딩) ────────────
_GGUF_DIR = _model_dir("gemma-4-26B-A4B-it-GGUF")
# IQ3_S = 3비트 최고 품질, 기본값
# IQ2_M / IQ2_XXS = 더 작은 메모리 필요 시 대체
LLAMA_GGUF_PATH = (
    _GGUF_DIR / "gemma-4-26B-A4B-it-UD-IQ3_S.gguf"
)
LLAMA_GGUF_PORT: int = 8031
LLAMA_N_CTX: int = 4096       # 컨텍스트 윈도우
LLAMA_N_THREADS: int = 8      # CPU 스레드 수

# E2B GGUF (F16 전체 정밀도 — VRAM ~4GB)
LLAMA_E2B_GGUF_PATH = _model_dir("gemma-4-E2B-it", "gemma-4-E2B-it-f16.gguf")
LLAMA_E2B_GGUF_PORT: int = 8032

# E4B GGUF (권장: Q4_K_M / 12GB 환경)
LLAMA_E4B_GGUF_PATH = _model_dir(
    "gemma-4-E4B-it-GGUF-1", "gemma-4-E4B-it-Q4_K_M.gguf"
)
LLAMA_E4B_GGUF_PORT: int = 8033
LLAMA_E4B_MMPROJ_PATH = _model_dir(
    "gemma-4-E4B-it-GGUF-1", "mmproj-F16.gguf"
)

# ── 공통 추론 파라미터 ────────────────────────────────
PROXY_PORT: int = 8000
QUANT_BITS: int = 4
MODEL_QUANT_BITS: dict[str, int] = {
    # 8GB 기본 정책: E2B는 int8 시작
    "gemma4-e2b": 8,
}
MODEL_FALLBACK_QUANT_BITS: dict[str, int] = {
    # 메모리 임계 시 int4 폴백
    "gemma4-e2b": 4,
}
MAX_NEW_TOKENS: int = 2048
DEFAULT_TEMPERATURE: float = 0.7
DEFAULT_TOP_P: float = 0.9
NLLB_MAX_LENGTH: int = 1024

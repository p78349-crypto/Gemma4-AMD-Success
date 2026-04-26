"""
GGUF / llama-server.exe (Vulkan) 서버 시작 스크립트.

- llama_gguf/bin/llama-server.exe (Vulkan 빌드) 직접 실행
- --ngl 99 : 전체 레이어를 AMD GPU(Vulkan)에 오프로드
- OpenAI 호환 /v1/chat/completions 자동 제공

지원 모델 패밀리:
  --family 26b  IQ3_S(10.4GB) / IQ2_M(9.3GB) / IQ2_XXS(9.2GB)  포트 8031
  --family e2b  F16(~4GB) 전체 정밀도                             포트 8032
  --family e4b  Q4_K_M(~4.6GB) / Q4_K_S(~4.5GB) / IQ2_M(~3.3GB) 포트 8033

실행 예시:
    python start.py                         # 26B IQ3_S 기본
    python start.py --model IQ2_M           # 26B VRAM 절약
    python start.py --family e2b            # E2B F16
    python start.py --ngl 0                 # CPU 전용
"""
import argparse
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from shared.config import (  # noqa: E402
    LLAMA_E2B_GGUF_PATH,
    LLAMA_E2B_GGUF_PORT,
    LLAMA_E4B_GGUF_PATH,
    LLAMA_E4B_MMPROJ_PATH,
    LLAMA_E4B_GGUF_PORT,
    LLAMA_GGUF_PATH,
    LLAMA_GGUF_PORT,
    LLAMA_N_CTX,
    LLAMA_N_THREADS,
)

_BIN_DIR = Path(__file__).resolve().parent / "bin"
_SERVER  = _BIN_DIR / "llama-server.exe"

# 패밀리별 GGUF 정보: {모델키: 파일명}
_FAMILY_MAP: dict[str, dict] = {
    "26b": {
        "dir": LLAMA_GGUF_PATH.parent,
        "default_model": "IQ3_S",
        "default_port":  LLAMA_GGUF_PORT,
        "models": {
            "IQ3_S":   "gemma-4-26B-A4B-it-UD-IQ3_S.gguf",
            "IQ2_M":   "gemma-4-26B-A4B-it-UD-IQ2_M.gguf",
            "IQ2_XXS": "gemma-4-26B-A4B-it-UD-IQ2_XXS.gguf",
        },
    },
    "e2b": {
        "dir": LLAMA_E2B_GGUF_PATH.parent,
        "default_model": "F16",
        "default_port":  LLAMA_E2B_GGUF_PORT,
        "models": {
            "F16": "gemma-4-E2B-it-f16.gguf",
        },
    },
    "e4b": {
        "dir": LLAMA_E4B_GGUF_PATH.parent,
        "default_model": "Q4_K_M",
        "default_port":  LLAMA_E4B_GGUF_PORT,
        "default_mmproj": "F16",
        "models": {
            "Q4_K_M": "gemma-4-E4B-it-Q4_K_M.gguf",
            "Q4_K_S": "gemma-4-E4B-it-Q4_K_S.gguf",
            "IQ2_M":  "gemma-4-E4B-it-UD-IQ2_M.gguf",
        },
        "mmproj": {
            "F16": LLAMA_E4B_MMPROJ_PATH.name,
            "BF16": "mmproj-BF16.gguf",
        },
    },
}


def _parse() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Gemma4 GGUF llama-server (Vulkan GPU)"
    )
    p.add_argument(
        "--family",
        choices=list(_FAMILY_MAP.keys()),
        default="26b",
        help="모델 패밀리 (기본: 26b)",
    )
    p.add_argument(
        "--model", default=None,
        help=(
            "양자화/버전 키 "
            "(26b: IQ3_S/IQ2_M/IQ2_XXS, e2b: F16, e4b: Q4_K_M/Q4_K_S/IQ2_M). "
            "미지정 시 패밀리 기본값"
        ),
    )
    p.add_argument(
        "--port", type=int, default=None,
        help="서버 포트 (미지정 시 패밀리 기본값)",
    )
    p.add_argument(
        "--n_ctx", type=int, default=LLAMA_N_CTX,
        help=f"컨텍스트 길이 (기본: {LLAMA_N_CTX})",
    )
    p.add_argument(
        "--n_threads", type=int, default=LLAMA_N_THREADS,
        help=f"CPU 스레드 수 (기본: {LLAMA_N_THREADS})",
    )
    p.add_argument(
        "--ngl", type=int, default=99,
        help="GPU 오프로드 레이어 수 (기본: 99=전체, 0=CPU전용)",
    )
    p.add_argument(
        "--mmproj",
        choices=["auto", "on", "off"],
        default="auto",
        help="비전용 mmproj 사용 (기본: auto, e4b에서 자동 연결)",
    )
    p.add_argument(
        "--mmproj_type",
        choices=["F16", "BF16"],
        default=None,
        help="mmproj 파일 타입 (기본: 패밀리 기본값)",
    )
    return p.parse_args()


def main() -> None:
    args = _parse()

    fam = _FAMILY_MAP[args.family]
    model_key = args.model if args.model else fam["default_model"]
    port      = args.port  if args.port  else fam["default_port"]

    if model_key not in fam["models"]:
        valid = ", ".join(fam["models"].keys())
        print(
            f"[오류] --family {args.family} 에서 유효한 --model: {valid}",
            file=sys.stderr,
        )
        sys.exit(1)

    if not _SERVER.exists():
        print(
            f"[오류] llama-server.exe 없음: {_SERVER}\n"
            "llama_gguf/bin/ 에 Vulkan 바이너리를 배치하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    model_file = fam["dir"] / fam["models"][model_key]
    if not model_file.exists():
        print(
            f"[오류] GGUF 파일 없음: {model_file}",
            file=sys.stderr,
        )
        sys.exit(1)

    mmproj_file: Path | None = None
    want_mmproj = (args.mmproj == "on") or (
        args.mmproj == "auto" and args.family == "e4b"
    )
    if want_mmproj and "mmproj" in fam:
        mmproj_key = (
            args.mmproj_type
            if args.mmproj_type
            else fam.get("default_mmproj", "F16")
        )
        mmproj_name = fam["mmproj"].get(mmproj_key)
        if not mmproj_name:
            print(
                f"[오류] 지원하지 않는 mmproj 타입: {mmproj_key}",
                file=sys.stderr,
            )
            sys.exit(1)
        mmproj_file = fam["dir"] / mmproj_name
        if not mmproj_file.exists():
            if args.mmproj == "on":
                print(
                    f"[오류] mmproj 파일 없음: {mmproj_file}",
                    file=sys.stderr,
                )
                sys.exit(1)
            mmproj_file = None

    backend = f"Vulkan GPU (ngl={args.ngl})" if args.ngl > 0 else "CPU"
    print(f"[GGUF] 패밀리 : {args.family.upper()}  ({model_key})")
    print(f"[GGUF] 모델   : {model_file.name}")
    print(
        "[GGUF] mmproj : "
        + (mmproj_file.name if mmproj_file else "없음(텍스트 전용)")
    )
    print(f"[GGUF] 포트   : {port}")
    print(f"[GGUF] ctx    : {args.n_ctx}")
    print(f"[GGUF] thread : {args.n_threads}")
    print(f"[GGUF] 백엔드 : {backend}")
    print()

    cmd = [
        str(_SERVER),
        "--model",        str(model_file),
        "--port",         str(port),
        "--ctx-size",     str(args.n_ctx),
        "--threads",      str(args.n_threads),
        "--n-gpu-layers", str(args.ngl),
        "--host",         "0.0.0.0",
        "--flash-attn",   "on",
        "--reasoning",    "off",
    ]
    if mmproj_file:
        cmd.extend(["--mmproj", str(mmproj_file)])

    proc = subprocess.Popen(cmd)
    try:
        sys.exit(proc.wait())
    except KeyboardInterrupt:
        sys.exit(proc.wait())


if __name__ == "__main__":
    main()

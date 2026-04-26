"""LLM 채팅 탭 — 실행 중인 LLM 서버와 대화 + 문서/이미지 첨부."""
import base64
import json
import os
import re
import shutil
import threading
import tkinter as tk
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from tkinter import filedialog
from urllib.error import URLError
from urllib.request import Request, urlopen

# ── 색상 ────────────────────────────────────────────
C_BG    = "#F5F5F5"
C_PANEL = "#FFFFFF"
C_TEXT  = "#212121"
C_SUB   = "#757575"
C_USER  = "#1565C0"
C_AI    = "#2E7D32"
C_SEND  = "#42A5F5"
C_STOP  = "#EF5350"
C_FILE  = "#F57C00"
C_IMG   = "#7B1FA2"

# 비전 서버 목록
VISION_SERVERS = {
    "[01]  Gemma4-E2B    :8001",
    "[02]  Gemma4-E4B    :8002",
    "[04]  InternVL2.5-4B :8004",
}

FONT      = ("맑은 고딕", 10)
FONT_B    = ("맑은 고딕", 10, "bold")
FONT_S    = ("맑은 고딕", 9)
FONT_CHAT = ("맑은 고딕", 10)

LLM_SERVERS = [
    ("[01]  Gemma4-E2B    :8001", 8001),
    ("[02]  Gemma4-E4B    :8002", 8002),
    ("[03]  Gemma4-26B    :8003", 8003),
    ("[04]  InternVL2.5-4B :8004", 8004),
    ("[05]  Gemma4-E2B GGUF F16   :8032", 8032),
    ("[06]  Gemma4-26B GGUF IQ3_S :8031", 8031),
    ("[07]  Gemma4-26B GGUF IQ2_M :8031", 8031),
]

# 문서 1회 전송 최대 글자 수 (너무 길면 컨텍스트 초과)
MAX_DOC_CHARS = 6000


def _default_server_label() -> str:
    """환경변수로 기본 서버 포트를 지정할 수 있게 한다."""
    default = LLM_SERVERS[0][0]
    raw = os.environ.get("VT_CHAT_DEFAULT_PORT", "").strip()
    if not raw.isdigit():
        return default
    port = int(raw)
    for name, p in LLM_SERVERS:
        if p == port:
            return name
    return default


# ── 문서 텍스트 추출 ─────────────────────────────────
def _read_txt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def _read_docx(path: str) -> str:
    with zipfile.ZipFile(path) as zf:
        xml_bytes = zf.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    lines = []
    for p in root.findall(".//w:p", ns):
        line = "".join(t.text or "" for t in p.findall(".//w:t", ns)).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def _read_epub(path: str) -> str:
    texts = []
    with zipfile.ZipFile(path) as zf:
        names = [n for n in zf.namelist()
                 if n.endswith((".html", ".xhtml", ".htm"))]
        # OPF 순서대로 정렬 시도
        try:
            opf = next(n for n in zf.namelist() if n.endswith(".opf"))
            opf_root = ET.fromstring(zf.read(opf))
            ns_opf = {"opf": "http://www.idpf.org/2007/opf"}
            spine = [
                item.get("idref")
                for item in opf_root.findall(".//opf:itemref", ns_opf)
            ]
            manifest = {
                item.get("id"): item.get("href")
                for item in opf_root.findall(".//opf:item", ns_opf)
            }
            base = str(Path(opf).parent)
            ordered = []
            for ref in spine:
                href = manifest.get(ref, "")
                full = f"{base}/{href}".lstrip("/") if base != "." else href
                if full in names:
                    ordered.append(full)
            names = ordered if ordered else names
        except Exception:
            pass
        for name in names:
            raw = zf.read(name).decode("utf-8", errors="replace")
            text = re.sub(r"<[^>]+>", "", raw)
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                texts.append(text)
    return "\n\n".join(texts)


def _read_srt(path: str) -> str:
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    result = []
    for line in lines:
        line = line.strip()
        if not line or line.isdigit() or "-->" in line:
            continue
        result.append(line)
    return "\n".join(result)


def _extract_text(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext in {".txt", ".md"}:
        return _read_txt(path)
    if ext == ".docx":
        return _read_docx(path)
    if ext == ".epub":
        return _read_epub(path)
    if ext in {".srt", ".svc"}:
        return _read_srt(path)
    return Path(path).read_text(encoding="utf-8", errors="replace")


def _is_alive(port: int) -> bool:
    for path in ("/health", "/v1/models"):
        try:
            urlopen(f"http://localhost:{port}{path}", timeout=1)
            return True
        except URLError as e:
            if getattr(e, "code", 0) in (405, 422):
                return True
        except Exception:
            pass
    return False


class ChatTab(tk.Frame):
    def __init__(self, master) -> None:
        super().__init__(master, bg=C_BG)
        self._history: list[dict] = []
        self._sent_images: list[str] = []
        self._sent_docs: list[str] = []
        self._streaming = False
        self._attached: str | None = None   # 문서 첨부 경로
        self._img_path: str | None = None   # 이미지 첨부 경로
        self._build_ui()

    # ── UI 구성 ────────────────────────────────────
    def _build_ui(self) -> None:
        # 서버 선택 바
        top = tk.Frame(self, bg=C_BG)
        top.pack(fill="x", padx=14, pady=(10, 4))

        tk.Label(top, text="LLM 서버:", font=FONT_B, bg=C_BG, fg=C_TEXT).pack(side="left")

        self._srv_var = tk.StringVar(value=_default_server_label())
        om = tk.OptionMenu(top, self._srv_var, *[n for n, _ in LLM_SERVERS])
        om.config(font=FONT, bg=C_PANEL, relief="solid", bd=1, highlightthickness=0)
        om.pack(side="left", padx=(6, 8))

        self._dot = tk.Label(top, text="●", font=FONT_B, bg=C_BG, fg="#BDBDBD")
        self._dot.pack(side="left")

        tk.Button(
            top, text="연결 확인", font=FONT_S,
            bg="#E0E0E0", relief="flat", cursor="hand2", pady=2,
            command=lambda: threading.Thread(
                target=self._check_conn, daemon=True).start(),
        ).pack(side="left", padx=(4, 0))

        tk.Button(
            top, text="대화 초기화", font=FONT_S,
            bg="#E0E0E0", relief="flat", cursor="hand2", pady=2,
            command=self._clear,
        ).pack(side="right")

        tk.Button(
            top, text="내보내기", font=FONT_S,
            bg="#E0E0E0", relief="flat", cursor="hand2", pady=2,
            command=self._export_chat,
        ).pack(side="right", padx=(0, 6))

        # 첨부 파일 바
        att = tk.Frame(self, bg=C_BG)
        att.pack(fill="x", padx=14, pady=(0, 4))

        tk.Button(
            att, text="📄 파일 첨부",
            font=FONT_S, bg="#FFF3E0", fg=C_FILE,
            activebackground="#FFE0B2",
            relief="solid", bd=1, cursor="hand2", pady=3,
            command=self._attach_file,
        ).pack(side="left")

        self._file_lbl = tk.Label(
            att, text="첨부 없음",
            font=FONT_S, bg=C_BG, fg=C_SUB,
        )
        self._file_lbl.pack(side="left", padx=(8, 4))

        self._file_clear_btn = tk.Button(
            att, text="✕",
            font=FONT_S, bg=C_BG, fg=C_STOP,
            relief="flat", cursor="hand2",
            command=self._clear_attach,
        )
        # 첨부 파일 있을 때만 표시

        # 이미지 첨부 버튼 (E4B 전용)
        self._img_btn = tk.Button(
            att, text="🖼 이미지 첨부",
            font=FONT_S, bg="#F3E5F5", fg=C_IMG,
            activebackground="#E1BEE7",
            relief="solid", bd=1, cursor="hand2", pady=3,
            command=self._attach_image,
        )
        self._img_btn.pack(side="left", padx=(6, 0))

        self._img_lbl = tk.Label(att, text="", font=FONT_S, bg=C_BG, fg=C_IMG)
        self._img_lbl.pack(side="left", padx=(4, 0))

        self._img_clear_btn = tk.Button(
            att, text="✕", font=FONT_S, bg=C_BG, fg=C_STOP,
            relief="flat", cursor="hand2",
            command=self._clear_img,
        )

        tk.Label(
            att,
            text="지원: .txt .md .docx .epub .srt",
            font=FONT_S, bg=C_BG, fg="#BDBDBD",
        ).pack(side="right")

        # 서버 변경 시 이미지 버튼 표시 제어
        self._srv_var.trace_add("write", self._on_srv_change)
        self._on_srv_change()

        # 채팅 영역
        cf = tk.Frame(self, bg=C_BG)
        cf.pack(fill="both", expand=True, padx=14, pady=(0, 6))

        self._chat = tk.Text(
            cf, font=FONT_CHAT,
            bg=C_PANEL, fg=C_TEXT,
            relief="solid", bd=1,
            wrap="word", state="disabled",
            padx=10, pady=8,
        )
        sb = tk.Scrollbar(cf, command=self._chat.yview)
        self._chat.configure(yscrollcommand=sb.set)
        self._chat.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._chat.tag_config("user",   foreground=C_USER,  font=FONT_B)
        self._chat.tag_config("ai",     foreground=C_AI,    font=FONT_B)
        self._chat.tag_config("msg",    foreground=C_TEXT,  font=FONT_CHAT)
        self._chat.tag_config("system", foreground=C_SUB,   font=FONT_S)
        self._chat.tag_config("file",   foreground=C_FILE,  font=FONT_S)

        # 입력 영역
        inp = tk.Frame(self, bg=C_BG)
        inp.pack(fill="x", padx=14, pady=(0, 4))

        self._input = tk.Text(
            inp, font=FONT,
            bg=C_PANEL, fg=C_TEXT,
            relief="solid", bd=1,
            height=3, wrap="word",
        )
        self._input.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._input.bind("<Return>",       self._on_enter)
        self._input.bind("<Shift-Return>", lambda e: None)

        btns = tk.Frame(inp, bg=C_BG)
        btns.pack(side="right")

        self._send_btn = tk.Button(
            btns, text="전송",
            font=FONT_B, bg=C_SEND, fg="white",
            activebackground=C_SEND, activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            width=6, pady=8,
            command=self._send,
        )
        self._send_btn.pack(fill="x", pady=(0, 4))

        self._stop_btn = tk.Button(
            btns, text="중단",
            font=FONT_B, bg=C_STOP, fg="white",
            activebackground=C_STOP, activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            width=6, pady=8,
            state="disabled",
            command=self._stop,
        )
        self._stop_btn.pack(fill="x")

        tk.Label(
            self,
            text="Enter = 전송   Shift+Enter = 줄바꿈",
            font=FONT_S, bg=C_BG, fg=C_SUB,
        ).pack(pady=(0, 6))

    # ── 파일 첨부 ──────────────────────────────────
    def _attach_file(self) -> None:
        path = filedialog.askopenfilename(
            title="첨부할 문서 선택",
            filetypes=[
                ("지원 문서", "*.txt *.md *.docx *.epub *.srt *.svc"),
                ("모든 파일", "*.*"),
            ],
        )
        if not path:
            return
        self._attached = path
        name = Path(path).name
        display = name if len(name) <= 30 else name[:27] + "..."
        self._file_lbl.config(text=f"📄 {display}", fg=C_FILE)
        self._file_clear_btn.pack(side="left")

    def _clear_attach(self) -> None:
        self._attached = None
        self._file_lbl.config(text="첨부 없음", fg=C_SUB)
        self._file_clear_btn.pack_forget()

    def _attach_image(self) -> None:
        path = filedialog.askopenfilename(
            title="첨부할 이미지 선택",
            filetypes=[
                ("이미지 파일", "*.jpg *.jpeg *.png *.webp *.bmp *.gif"),
                ("모든 파일", "*.*"),
            ],
        )
        if not path:
            return
        self._img_path = path
        name = Path(path).name
        display = name if len(name) <= 24 else name[:21] + "..."
        self._img_lbl.config(text=f"🖼 {display}")
        self._img_clear_btn.pack(side="left")

    def _clear_img(self) -> None:
        self._img_path = None
        self._img_lbl.config(text="")
        self._img_clear_btn.pack_forget()

    def _on_srv_change(self, *_) -> None:
        is_vision = self._srv_var.get() in VISION_SERVERS
        if is_vision:
            self._img_btn.pack(side="left", padx=(6, 0))
        else:
            self._img_btn.pack_forget()
            self._clear_img()

    # ── 연결 확인 ──────────────────────────────────
    def _port(self) -> int:
        name = self._srv_var.get()
        return next(p for n, p in LLM_SERVERS if n == name)

    def _check_conn(self) -> None:
        port = self._port()
        alive = _is_alive(port)
        color = "#4CAF50" if alive else C_STOP
        msg   = f"포트 {port} {'연결됨 ✓' if alive else '미실행 ✗'}"
        self.after(0, self._dot.config, {"fg": color})
        self.after(0, self._sys, msg)

    # ── 전송 ───────────────────────────────────────
    def _on_enter(self, event) -> str:
        if not (event.state & 0x1):
            self._send()
            return "break"

    def _send(self) -> None:
        if self._streaming:
            return
        text = self._input.get("1.0", "end").strip()
        if not text and not self._attached and not self._img_path:
            return
        self._input.delete("1.0", "end")

        # 문서 첨부 처리
        doc_context = ""
        if self._attached:
            try:
                raw = _extract_text(self._attached)
                if len(raw) > MAX_DOC_CHARS:
                    raw = raw[:MAX_DOC_CHARS] + f"\n...(이하 생략, 총 {len(raw)}자)"
                fname = Path(self._attached).name
                doc_context = f"[첨부 문서: {fname}]\n{raw}\n\n"
                self._sys(f"📄 문서 첨부: {fname}  ({len(raw)}자)")
                self._sent_docs.append(self._attached)
            except Exception as e:
                self._sys(f"[오류] 문서 읽기 실패: {e}")
                return
            self._clear_attach()

        # 이미지 첨부 처리 (E4B 전용 — content list 형식)
        img_part = None
        if self._img_path:
            try:
                img_src = self._img_path
                ext = Path(self._img_path).suffix.lower().lstrip(".")
                mime = "jpeg" if ext in ("jpg", "jpeg") else ext
                with open(self._img_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                img_part = {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/{mime};base64,{b64}"},
                }
                self._sys(f"🖼 이미지 첨부: {Path(self._img_path).name}")
                self._sent_images.append(img_src)
            except Exception as e:
                self._sys(f"[오류] 이미지 읽기 실패: {e}")
                return
            self._clear_img()

        # content 조합
        if img_part:
            parts = [img_part]
            combined_text = (doc_context + text).strip() if (doc_context or text) else ""
            if combined_text:
                parts.append({"type": "text", "text": combined_text})
            full_content = parts
            display_text = f"🖼 이미지 첨부\n{text}" if text else "🖼 이미지 첨부"
        else:
            full_content = doc_context + text if text else doc_context.rstrip()
            display_text = (
                f"📄 문서 첨부\n{text}" if doc_context and text
                else ("📄 문서 첨부" if doc_context else text)
            )

        self._history.append({"role": "user", "content": full_content})
        self._append("나", display_text, "user")
        self._append("AI", "", "ai")
        self._busy(True)
        threading.Thread(target=self._stream, daemon=True).start()

    # ── 스트리밍 ───────────────────────────────────
    def _stream(self) -> None:
        port = self._port()
        body = json.dumps({
            "model": "gemma",
            "messages": self._history,
            "stream": True,
        }).encode("utf-8")
        req = Request(
            f"http://localhost:{port}/v1/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        full = ""
        try:
            with urlopen(req, timeout=120) as resp:
                for raw in resp:
                    if not self._streaming:
                        break
                    line = raw.decode("utf-8", errors="replace").strip()
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        delta = (
                            json.loads(data)["choices"][0]["delta"]
                            .get("content", "")
                        )
                        if delta:
                            full += delta
                            self.after(0, self._delta, delta)
                    except Exception:
                        pass
        except Exception as e:
            self.after(0, self._sys, f"[오류] {e}")

        if full:
            self._history.append({"role": "assistant", "content": full})
        self.after(0, self._nl)
        self.after(0, self._busy, False)

    def _stop(self) -> None:
        self._streaming = False

    def _busy(self, on: bool) -> None:
        self._streaming = on
        self._send_btn.configure(state="disabled" if on else "normal")
        self._stop_btn.configure(state="normal" if on else "disabled")

    # ── 텍스트 출력 ────────────────────────────────
    def _append(self, who: str, text: str, tag: str) -> None:
        self._chat.configure(state="normal")
        self._chat.insert("end", f"\n{who}\n", tag)
        if text:
            self._chat.insert("end", text + "\n", "msg")
        self._chat.see("end")
        self._chat.configure(state="disabled")

    def _delta(self, text: str) -> None:
        self._chat.configure(state="normal")
        self._chat.insert("end", text, "msg")
        self._chat.see("end")
        self._chat.configure(state="disabled")

    def _nl(self) -> None:
        self._chat.configure(state="normal")
        self._chat.insert("end", "\n")
        self._chat.configure(state="disabled")

    def _sys(self, text: str) -> None:
        self._chat.configure(state="normal")
        self._chat.insert("end", f"\n{text}\n", "system")
        self._chat.see("end")
        self._chat.configure(state="disabled")

    def _clear(self) -> None:
        self._history.clear()
        self._sent_images.clear()
        self._sent_docs.clear()
        self._chat.configure(state="normal")
        self._chat.delete("1.0", "end")
        self._chat.configure(state="disabled")
        self._clear_attach()
        self._clear_img()

    def _export_chat(self) -> None:
        text = self._chat.get("1.0", "end").strip()
        if not text:
            self._sys("[안내] 내보낼 대화가 없습니다.")
            return

        path = filedialog.asksaveasfilename(
            title="채팅 내보내기",
            defaultextension=".md",
            filetypes=[
                ("Markdown", "*.md"),
                ("텍스트", "*.txt"),
            ],
        )
        if not path:
            return

        out = Path(path)
        assets_dir = out.parent / f"{out.stem}_assets"
        copied_imgs: list[str] = []
        copied_docs: list[str] = []

        # 첨부 자산이 있으면 별도 폴더로 함께 저장
        for src in self._sent_images:
            p = Path(src)
            if p.exists():
                assets_dir.mkdir(parents=True, exist_ok=True)
                dst = assets_dir / p.name
                if not dst.exists():
                    shutil.copy2(p, dst)
                copied_imgs.append(dst.name)

        for src in self._sent_docs:
            p = Path(src)
            if p.exists():
                assets_dir.mkdir(parents=True, exist_ok=True)
                dst = assets_dir / p.name
                if not dst.exists():
                    shutil.copy2(p, dst)
                copied_docs.append(dst.name)

        if out.suffix.lower() == ".txt":
            lines = [text, ""]
            if copied_docs:
                lines.append("[첨부 문서]")
                lines.extend(f"- {name}" for name in copied_docs)
                lines.append("")
            if copied_imgs:
                lines.append("[첨부 이미지]")
                lines.extend(f"- {name}" for name in copied_imgs)
                lines.append("")
            out.write_text("\n".join(lines), encoding="utf-8")
        else:
            lines = ["# 채팅 내보내기", "", "## 대화", "", text, ""]
            if copied_docs:
                lines.extend(["## 첨부 문서", ""])
                lines.extend(
                    f"- [{name}]({assets_dir.name}/{name})" for name in copied_docs
                )
                lines.append("")
            if copied_imgs:
                lines.extend(["## 첨부 이미지", ""])
                lines.extend(
                    f"- ![{name}]({assets_dir.name}/{name})" for name in copied_imgs
                )
                lines.append("")
            out.write_text("\n".join(lines), encoding="utf-8")

        self._sys(f"[완료] 내보내기: {out}")

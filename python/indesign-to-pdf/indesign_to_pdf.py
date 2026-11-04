"""
Scarica le pagine di una pubblicazione Adobe Publish Online e le
trasforma in PDF usando un browser Chromium/Edge/Chrome in modalità
headless. Richiede Python 3.9+, `requests` e un browser Chromium (o Playwright).

Uso rapido:
    python indesign_to_pdf.py --pub-id 9fffdfc4-55ed-43b2-93cd-4bcf5f53a412
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple

import requests

try:
    from PyPDF2 import PdfMerger  # type: ignore
except ImportError:  # pragma: no cover - opzionale
    PdfMerger = None

MANIFEST_API = "https://indd.adobe.com/api/v1/getManifestdata"
PAGE_BASE = "https://indd.adobe.com/view/publication"

DEFAULT_BROWSER_CANDIDATES = [
    # Windows
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    # macOS
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    # Linux / PATH
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
    "chrome.exe",
    "msedge.exe",
]


class DownloadError(RuntimeError):
    """Errore custom per download falliti."""


class PageJob(NamedTuple):
    index: int
    url: str
    width: float
    height: float
    output: Path


def detect_browser(explicit_path: Optional[str]) -> Path:
    """Restituisce il percorso di Chrome/Edge da usare in headless."""
    if explicit_path:
        path = Path(explicit_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Browser non trovato: {path}")
        return path

    for candidate in DEFAULT_BROWSER_CANDIDATES:
        path = Path(candidate)
        if not path.is_absolute():
            resolved = shutil.which(candidate)
            if resolved:
                return Path(resolved)
        elif path.exists():
            return path

    raise FileNotFoundError(
        "Impossibile trovare Chrome/Edge. Specifica --browser-path oppure installa "
        "Chrome o Microsoft Edge."
    )


def fetch_manifest(pub_id: str, session: Optional[requests.Session] = None) -> Tuple[dict, str]:
    sess = session or requests.Session()
    resp = sess.get(MANIFEST_API, params={"pubId": pub_id}, timeout=20)
    if resp.status_code != 200:
        raise DownloadError(f"Manifest API error {resp.status_code}: {resp.text[:200]}")
    payload = resp.json()
    if "data" not in payload or "activeVersion" not in payload:
        raise DownloadError("Manifest JSON incompleto.")
    return payload["data"], payload["activeVersion"]


def build_page_url(pub_id: str, version: str, page_html: str) -> str:
    return f"{PAGE_BASE}/{pub_id}/{version}/{page_html}"


def parse_px(value, fallback: float) -> float:
    if isinstance(value, (int, float)):
        try:
            return float(value)
        except (TypeError, ValueError):
            return fallback
    if isinstance(value, str):
        txt = value.strip().lower()
        if txt.endswith("px"):
            txt = txt[:-2]
        try:
            return float(txt)
        except ValueError:
            return fallback
    return fallback


def headless_print(
    browser_path: Path,
    url: str,
    output_pdf: Path,
    extra_wait: float = 1.5,
    virtual_time_budget_ms: int = 15000,
) -> None:
    """Apre l'URL nel browser headless e lo stampa in PDF."""
    # Chrome/Edge headless richiede percorsi assoluti, altrimenti tenta di
    # risolverli rispetto alla propria working dir (che non è la nostra).
    output_pdf = output_pdf.resolve()
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    print(f"    writing -> {output_pdf}")

    cmd = [
        str(browser_path),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--virtual-time-budget={virtual_time_budget_ms}",
        f"--print-to-pdf={output_pdf}",
        url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not output_pdf.exists():
        raise RuntimeError(
            f"Stampa headless fallita ({result.returncode}):\n"
            f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )

    # Attesa extra per sicurezza (Chromium può terminare prima di flush)
    if extra_wait > 0:
        time.sleep(extra_wait)


def render_with_playwright(jobs: List[PageJob], timeout_ms: int) -> List[Path]:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError as exc:  # pragma: no cover - opzionale
        raise RuntimeError(
            "Playwright non è installato. Installa con `pip install playwright` "
            "e scarica il browser con `python -m playwright install chromium`, "
            "oppure usa --renderer chrome."
        ) from exc

    rendered: List[Path] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        for job in jobs:
            print(f"[{job.index+1}] Playwright rendering {job.url}")
            page = context.new_page()
            viewport = {
                "width": max(1, int(round(job.width))),
                "height": max(1, int(round(job.height))),
            }
            page.set_viewport_size(viewport)
            page.goto(job.url, wait_until="networkidle", timeout=timeout_ms + 5000)
            pdf_kwargs = dict(
                path=str(job.output),
                width=f"{job.width}px",
                height=f"{job.height}px",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                prefer_css_page_size=True,
            )
            job.output.parent.mkdir(parents=True, exist_ok=True)
            page.pdf(**pdf_kwargs)
            rendered.append(job.output)
            page.close()
        browser.close()
    return rendered


def merge_pdfs(pdf_files: List[Path], merged_path: Path) -> None:
    if not PdfMerger:
        raise RuntimeError(
            "PyPDF2 non è installato: impossibile unire i PDF. "
            "Installa con `pip install PyPDF2` oppure usa --no-merge."
        )

    merger = PdfMerger()
    try:
        for pdf in pdf_files:
            merger.append(str(pdf))
        merged_path.parent.mkdir(parents=True, exist_ok=True)
        merger.write(str(merged_path))
    finally:
        merger.close()


def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scarica e converte in PDF una pubblicazione Adobe Publish Online."
    )
    parser.add_argument(
        "--pub-id",
        required=True,
        help="ID della pubblicazione (ultimo segmento del link indd.adobe.com/view/...).",
    )
    parser.add_argument(
        "--browser-path",
        help="Percorso di Chrome/Microsoft Edge. Se omesso, il tool prova a individuarlo.",
    )
    parser.add_argument(
        "--output-dir",
        default="output_pages",
        help="Cartella dove salvare i PDF delle singole pagine.",
    )
    parser.add_argument(
        "--merged-pdf",
        default="catalogo.pdf",
        help="Nome del PDF finale (se l'unione è abilitata).",
    )
    parser.add_argument(
        "--no-merge",
        action="store_true",
        help="Non unire i PDF delle singole pagine.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        help="Limita il numero di pagine da scaricare (debug/test).",
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=0,
        help="Indice di pagina iniziale (0 = prima pagina).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15000,
        help="Virtual time budget in millisecondi per il rendering headless.",
    )
    parser.add_argument(
        "--renderer",
        choices=("chrome", "playwright"),
        default="playwright",
        help="Motore di rendering: 'playwright' mantiene le dimensioni originali della pagina.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_cli()

    try:
        manifest, active_version = fetch_manifest(args.pub_id)
    except Exception as exc:  # pragma: no cover - rete
        print(f"Errore nel download del manifest: {exc}", file=sys.stderr)
        return 3

    pages = manifest.get("pages", [])
    if not pages:
        print("Manifest senza pagine.", file=sys.stderr)
        return 4

    start = max(0, args.start_page)
    end = len(pages)
    if args.max_pages:
        end = min(end, start + args.max_pages)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    jobs: List[PageJob] = []
    total = len(pages)
    for idx, page in enumerate(pages[start:end], start=start):
        page_url = build_page_url(args.pub_id, active_version, page["html"])
        page_pdf = output_dir / f"page-{idx:04d}.pdf"
        width_px = parse_px(page.get("width"), 595.0)
        height_px = parse_px(page.get("height"), 842.0)
        jobs.append(PageJob(index=idx, url=page_url, width=width_px, height=height_px, output=page_pdf))

    generated_files: List[Path] = []
    if args.renderer == "playwright":
        try:
            generated_files = render_with_playwright(jobs, args.timeout)
        except Exception as exc:
            print(f"Errore Playwright: {exc}", file=sys.stderr)
            return 5
    else:
        try:
            browser = detect_browser(args.browser_path)
        except FileNotFoundError as exc:
            print(str(exc), file=sys.stderr)
            return 2

        for job in jobs:
            print(f"[{job.index+1}/{total}] Rendering {job.url} -> {job.output}")
            try:
                headless_print(
                    browser,
                    job.url,
                    job.output,
                    virtual_time_budget_ms=args.timeout,
                )
            except Exception as exc:
                print(f"  ERRORE pagina {job.index}: {exc}", file=sys.stderr)
                continue
            generated_files.append(job.output)

    if not generated_files:
        print("Nessuna pagina convertita con successo.", file=sys.stderr)
        return 5

    if args.no_merge:
        print(f"PDF salvati in {output_dir}. Unione disabilitata.")
        return 0

    merged_path = Path(args.merged_pdf)
    try:
        merge_pdfs(generated_files, merged_path)
    except Exception as exc:
        print(f"Unione PDF fallita: {exc}", file=sys.stderr)
        print("I PDF singoli sono comunque disponibili.", file=sys.stderr)
        return 6

    print(f"PDF finale creato: {merged_path.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


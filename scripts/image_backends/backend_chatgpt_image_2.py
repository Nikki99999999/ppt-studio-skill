#!/usr/bin/env python3
"""
ChatGPT Image 2.0 Backend (via Browser Automation)

Generates images by driving ChatGPT's web UI through CDP (Chrome DevTools Protocol).
Leverages the user's existing ChatGPT Plus/Max membership — no API key required.

Key advantage over OpenAI / DALL-E: accurate Chinese text rendering.

Configuration keys (env or .env):
  CHATGPT_IMAGE_TOOL         (optional) Override path to chatgpt_image.js
                              Default: <workspace>/.claude/skills/context-infrastructure/tools/chatgpt_image.js
  CHATGPT_IMAGE_TIMEOUT      (optional) Per-call timeout in seconds (default: 360)
  CDP_PROXY_URL              (optional) CDP proxy URL (default: http://localhost:3456)

Prerequisites:
  - Node.js >= 22
  - Chrome with --remote-debugging-port=9222
  - CDP Proxy running (web-access skill)
  - User logged into chatgpt.com in Chrome
"""

import os
import shutil
import subprocess
import time
from pathlib import Path

from image_backends.backend_common import (
    is_rate_limit_error,
    resolve_output_path,
    retry_delay,
)


DEFAULT_TIMEOUT = 360  # 6 min — covers thinking (60s) + rendering (240s) + buffer
NEEDS_MANUAL_EXIT_CODE = 3


class NeedsManualImageError(RuntimeError):
    """Raised when browser generation should be handed to a human operator."""

# ──────────────────────────────────────────────────────────────────
#  Tool discovery
# ──────────────────────────────────────────────────────────────────


def _resolve_tool_path() -> Path:
    """
    Locate chatgpt_image.js. Priority:
      1. CHATGPT_IMAGE_TOOL env var (absolute path)
      2. Default location relative to this backend file
    """
    explicit = os.environ.get("CHATGPT_IMAGE_TOOL")
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(
                f"CHATGPT_IMAGE_TOOL points to a non-existent file: {path}"
            )
        return path

    # Default path: prefer the shared workspace tool, then the legacy skill copy.
    # Layout: .claude/skills/ppt-studio/skills/ppt-studio/scripts/image_backends/backend_chatgpt_image_2.py
    # Target: <workspace>/context-infrastructure/tools/chatgpt_image.js
    here = Path(__file__).resolve()
    workspace_root = here.parents[7]
    skills_root = here.parents[5]  # .claude/skills
    candidates = [
        workspace_root / "context-infrastructure" / "tools" / "chatgpt_image.js",
        skills_root / "context-infrastructure" / "tools" / "chatgpt_image.js",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "chatgpt_image.js not found. Either:\n"
        f"  1. Keep the workspace tool at: {candidates[0]}\n"
        f"  2. Install context-infrastructure skill at: {skills_root / 'context-infrastructure'}\n"
        "  3. Or set CHATGPT_IMAGE_TOOL=/absolute/path/to/chatgpt_image.js in .env"
    )


def _ensure_node_available() -> None:
    """Verify Node.js is installed and on PATH."""
    if shutil.which("node") is None:
        raise RuntimeError(
            "Node.js not found on PATH. Install Node.js >= 22 to use the ChatGPT Image 2.0 backend."
        )


# ──────────────────────────────────────────────────────────────────
#  Prompt composition
# ──────────────────────────────────────────────────────────────────


def _compose_prompt(prompt: str, negative_prompt: str = None,
                    aspect_ratio: str = None) -> str:
    """
    ChatGPT Image 2.0 reads natural language. Inline aspect ratio + negative
    cues into the prompt since the web UI has no separate fields.
    """
    parts = [prompt.strip()]

    if aspect_ratio and aspect_ratio != "1:1":
        parts.append(f"Aspect ratio: {aspect_ratio}.")

    if negative_prompt:
        parts.append(f"Avoid: {negative_prompt.strip()}.")

    return " ".join(parts)


# ──────────────────────────────────────────────────────────────────
#  Subprocess invocation
# ──────────────────────────────────────────────────────────────────


def _invoke_tool(tool_path: Path, prompt: str, output_path: str,
                 timeout: int) -> None:
    """Run chatgpt_image.js as a subprocess. Raises on failure."""
    cmd = [
        "node",
        str(tool_path),
        "--prompt", prompt,
        "--output", output_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            f"ChatGPT Image 2.0 generation timed out after {timeout}s"
        ) from exc

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        detail = stderr or stdout or "(no output)"
        if result.returncode == NEEDS_MANUAL_EXIT_CODE:
            raise NeedsManualImageError(detail)
        raise RuntimeError(f"chatgpt_image.js failed: {detail}")

    if not Path(output_path).exists():
        raise RuntimeError(
            f"chatgpt_image.js reported success but output file is missing: {output_path}"
        )


# ──────────────────────────────────────────────────────────────────
#  Public API
# ──────────────────────────────────────────────────────────────────


def generate(prompt: str, negative_prompt: str = None,
             aspect_ratio: str = "1:1", image_size: str = "1K",
             output_dir: str = None, filename: str = None,
             model: str = None, max_retries: int = 0) -> str:
    """
    Generate an image with ChatGPT Image 2.0 via browser automation.

    Args:
        prompt: Positive prompt text
        negative_prompt: Negative prompt (folded into the prompt as "Avoid: ...")
        aspect_ratio: Aspect ratio hint (folded into the prompt; ChatGPT decides actual size)
        image_size: Ignored — ChatGPT returns ~1K natively (1024x1024 / 1792x1024)
        output_dir: Output directory
        filename: Output filename (without extension)
        model: Ignored — this backend is pinned to the verified chatgpt-image-2 adapter
        max_retries: Maximum retry count. Default is 0 because web generation is expensive
            and a 5 min watchdog hands off to a human instead of resubmitting.

    Returns:
        Absolute path of the saved image file
    """
    _ensure_node_available()
    tool_path = _resolve_tool_path()

    if model and model.strip().lower() not in {"chatgpt-image-2", "image-2", "gpt-image-2"}:
        raise ValueError(
            "chatgpt-image-2 backend is strict: it only satisfies Image 2.0 requests. "
            f"Requested model: {model}"
        )

    timeout_str = os.environ.get("CHATGPT_IMAGE_TIMEOUT")
    timeout = int(timeout_str) if timeout_str else DEFAULT_TIMEOUT

    output_path = resolve_output_path(prompt, output_dir, filename, ".jpg")
    full_prompt = _compose_prompt(prompt, negative_prompt, aspect_ratio)

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            _invoke_tool(tool_path, full_prompt, output_path, timeout)
            return output_path
        except NeedsManualImageError:
            raise
        except Exception as exc:
            last_error = exc
            if attempt >= max_retries:
                break
            limited = is_rate_limit_error(exc)
            delay = retry_delay(attempt, rate_limited=limited)
            label = "Rate limited" if limited else f"Error: {exc}"
            print(f"\n  [WARN] {label}. Retrying in {delay}s "
                  f"(attempt {attempt + 1}/{max_retries})...")
            time.sleep(delay)

    raise RuntimeError(
        f"ChatGPT Image 2.0 generation failed after {max_retries + 1} attempts: {last_error}"
    )

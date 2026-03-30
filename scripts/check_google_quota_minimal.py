"""Minimal Google API quota probe: one request, no retries."""

import json
import os
import time


def _load_dotenv_file(env_path: str) -> None:
    """Load key=value pairs from .env into os.environ if missing."""
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def main() -> int:
    _load_dotenv_file(".env")

    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    model = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"

    if not api_key:
        print(json.dumps({
            "ok": False,
            "reason": "missing_google_api_key",
        }, ensure_ascii=False))
        return 2

    started = time.time()

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        # Single minimal request to avoid quota waste.
        response = client.models.generate_content(
            model=model,
            contents="ping",
            config={"max_output_tokens": 1, "temperature": 0.0},
        )

        elapsed = round(time.time() - started, 3)
        text = getattr(response, "text", None)

        print(json.dumps({
            "ok": True,
            "status": "quota_available",
            "model": model,
            "elapsed_sec": elapsed,
            "preview": (text or "")[:80],
        }, ensure_ascii=False))
        return 0

    except Exception as exc:  # noqa: BLE001
        elapsed = round(time.time() - started, 3)
        message = str(exc)
        low = message.lower()

        quota_blocked = (
            "resource_exhausted" in low
            or "quota" in low
            or "429" in low
            or "rate limit" in low
        )

        print(json.dumps({
            "ok": False,
            "status": "quota_blocked" if quota_blocked else "request_failed",
            "model": model,
            "elapsed_sec": elapsed,
            "error": message[:500],
        }, ensure_ascii=False))
        return 1 if quota_blocked else 3


if __name__ == "__main__":
    raise SystemExit(main())

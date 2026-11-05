import asyncio
import hmac
import json
import logging
import os
import time

import httpx
from fastapi import FastAPI, Request, Response

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("gateway")

PROVIDER_URL = os.environ.get(
    "TEAM_PROVIDER_URL",
    "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
)
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.1"))
REASONING = os.environ.get("GEMINI_REASONING_EFFORT", "none")  # "" to omit
OUTPUT_CAP = int(os.environ.get("MAX_OUTPUT_CAP", "1024"))
FALLBACK_TEXT = os.environ.get("FALLBACK_TEXT", "")
MAX_BODY = 65536

app = FastAPI()

client = httpx.AsyncClient(timeout=20.0, follow_redirects=False, trust_env=False)
limiter = asyncio.Semaphore(8)


def reply(obj, status=200):
    return Response(content=json.dumps(obj), status_code=status,
                    media_type="application/json")


def fallback():
    if not FALLBACK_TEXT:
        return reply({"error": "Team gateway unavailable"}, 503)
    return reply({"text": FALLBACK_TEXT, "usage": {}})


def parse_frame(raw: bytes):
    if not 0 < len(raw) <= MAX_BODY:
        raise ValueError("size")
    frame = json.loads(raw)
    if not isinstance(frame, dict) or set(frame) != {"messages", "max_output_tokens"}:
        raise ValueError("keys")
    msgs, mot = frame["messages"], frame["max_output_tokens"]
    if not isinstance(msgs, list) or not 1 <= len(msgs) <= 24:
        raise ValueError("messages")
    if type(mot) is not int or not 16 <= mot <= 2048:
        raise ValueError("max_output_tokens")
    return msgs, mot


async def call_provider(payload, key):
    headers = {"Authorization": "Bearer " + key}
    for attempt in range(2):
        try:
            r = await client.post(PROVIDER_URL, json=payload, headers=headers)
            if r.status_code == 429 or r.status_code >= 500:
                log.info("provider status %s (attempt %d)", r.status_code, attempt + 1)
                await asyncio.sleep(1)
                continue
            if r.status_code >= 400:
                log.info("provider rejected: status %s body=%s", r.status_code, r.text[:300])
            r.raise_for_status()
            return r.json()
        except (httpx.TimeoutException, httpx.TransportError) as e:
            log.info("provider %s (attempt %d)", type(e).__name__, attempt + 1)
    raise RuntimeError("provider failed")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/gateway")
async def gateway(request: Request):
    start = time.perf_counter()
    status = "ok"
    try:
        token = os.environ.get("TEAM_GATEWAY_TOKEN", "")
        auth = request.headers.get("authorization", "")
        if not token or not hmac.compare_digest(auth.encode(), ("Bearer " + token).encode()):
            status = "403"
            return Response(status_code=403)

        try:
            msgs, mot = parse_frame(await request.body())
        except Exception:
            status = "400"
            return reply({"error": "bad request"}, 400)

        key = os.environ.get("GEMINI_API_KEY", "")
        if not key:
            status = "no_key"
            return fallback()

        payload = {"model": MODEL, "messages": msgs,
                   "max_tokens": min(mot, OUTPUT_CAP), "temperature": TEMPERATURE}
        if REASONING:
            payload["reasoning_effort"] = REASONING

        async with limiter:
            result = await asyncio.wait_for(call_provider(payload, key), timeout=40)

        text = result["choices"][0]["message"]["content"]
        if not isinstance(text, str) or not 0 < len(text.encode()) <= 65536:
            raise ValueError("bad text")
        usage = result.get("usage") or {}
        out = {o: usage[k] for k, o in (("prompt_tokens", "input_tokens"),
                                        ("completion_tokens", "output_tokens"))
               if type(usage.get(k)) is int and usage[k] >= 0}
        return reply({"text": text, "usage": out})
    except Exception as e:
        status = "fallback:" + type(e).__name__
        return fallback()
    finally:
        log.info("POST /gateway result=%s latency=%.2fs", status, time.perf_counter() - start)
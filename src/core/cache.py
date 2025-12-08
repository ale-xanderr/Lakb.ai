# src/core/cache.py
import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from core.config import Config

CACHE_DIR = Config.CACHE_DIR
CACHE_EXPIRY = timedelta(hours=Config.CACHE_EXPIRY_HOURS)

def _ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def _key_to_filename(key: str) -> str:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{digest}.json")

def set_cache(key: str, payload: dict):
    _ensure_dir(CACHE_DIR)
    fn = _key_to_filename(key)
    payload_wrapped = {
        "_cached_at": datetime.utcnow().isoformat(),
        "payload": payload
    }
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(payload_wrapped, f, ensure_ascii=False, indent=2)

def get_cache(key: str) -> Optional[dict]:
    fn = _key_to_filename(key)
    if not os.path.exists(fn):
        return None
    try:
        with open(fn, "r", encoding="utf-8") as f:
            data = json.load(f)
        cached_at = datetime.fromisoformat(data.get("_cached_at"))
        if datetime.utcnow() - cached_at > CACHE_EXPIRY:
            try:
                os.remove(fn)
            except Exception:
                pass
            return None
        return data.get("payload")
    except Exception:
        return None

def clear_cache():
    _ensure_dir(CACHE_DIR)
    for fname in os.listdir(CACHE_DIR):
        path = os.path.join(CACHE_DIR, fname)
        try:
            os.remove(path)
        except Exception:
            pass

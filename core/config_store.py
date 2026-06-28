"""Read/write persistence for global config, templates and run history.

All state lives as JSON files under the ``data/`` directory so that templates
and configuration survive app restarts (PRD §6 Persistence, §7 Data Flow).
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUTS_DIR = BASE_DIR / "outputs"

CONFIG_PATH = DATA_DIR / "config.json"
TEMPLATES_PATH = DATA_DIR / "templates.json"
HISTORY_PATH = DATA_DIR / "runs_history.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "brand_name": "",
    "brand_logo_path": "",
    "region": "ir",
    "language": "fa",
    "device": "desktop",
    "num_pages": 1,
    "delay_ms": 200,
    "proxy": "",
}

# Keys that must never be written to the shared config file (PRD §6 Security).
# The Serper API key lives only in per-session state (see core/secrets.py).
SECRET_KEYS = {"serper_api_key"}


def _ensure_dirs() -> None:
    for d in (DATA_DIR, ASSETS_DIR, OUTPUTS_DIR):
        d.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return fallback


def _write_json(path: Path, payload: Any) -> None:
    _ensure_dirs()
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    tmp.replace(path)


# --------------------------------------------------------------------------- #
# Global configuration
# --------------------------------------------------------------------------- #
def load_config() -> dict[str, Any]:
    cfg = dict(DEFAULT_CONFIG)
    stored = _read_json(CONFIG_PATH, {})
    # Defensively strip any secret that an older file version may have saved.
    for k in SECRET_KEYS:
        stored.pop(k, None)
    cfg.update(stored)
    return cfg


def save_config(config: dict[str, Any]) -> None:
    merged = dict(DEFAULT_CONFIG)
    merged.update(config)
    for k in SECRET_KEYS:
        merged.pop(k, None)  # never persist secrets to the shared file
    _write_json(CONFIG_PATH, merged)


def is_brand_configured(config: dict[str, Any]) -> bool:
    """Non-secret readiness check (brand identity). The API key is checked
    separately via core.secrets because it is session-scoped."""
    return bool(config.get("brand_name"))


# --------------------------------------------------------------------------- #
# Templates
# --------------------------------------------------------------------------- #
def load_templates() -> list[dict[str, Any]]:
    return _read_json(TEMPLATES_PATH, [])


def save_templates(templates: list[dict[str, Any]]) -> None:
    _write_json(TEMPLATES_PATH, templates)


def add_template(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        raise ValueError("Template text cannot be empty.")
    templates = load_templates()
    record = {"id": uuid.uuid4().hex, "text": text}
    templates.append(record)
    save_templates(templates)
    return record


def update_template(template_id: str, text: str) -> None:
    text = text.strip()
    if not text:
        raise ValueError("Template text cannot be empty.")
    templates = load_templates()
    for tpl in templates:
        if tpl["id"] == template_id:
            tpl["text"] = text
            break
    save_templates(templates)


def delete_template(template_id: str) -> None:
    templates = [t for t in load_templates() if t["id"] != template_id]
    save_templates(templates)


# --------------------------------------------------------------------------- #
# Run history
# --------------------------------------------------------------------------- #
def load_history() -> list[dict[str, Any]]:
    return _read_json(HISTORY_PATH, [])


def add_history_entry(entry: dict[str, Any]) -> None:
    history = load_history()
    history.insert(0, entry)
    _write_json(HISTORY_PATH, history)


def new_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_logo(uploaded_file) -> str:
    """Persist an uploaded logo to assets/ and return its path."""
    _ensure_dirs()
    suffix = Path(uploaded_file.name).suffix or ".png"
    dest = ASSETS_DIR / f"brand_logo{suffix}"
    with dest.open("wb") as fh:
        fh.write(uploaded_file.getbuffer())
    return str(dest)

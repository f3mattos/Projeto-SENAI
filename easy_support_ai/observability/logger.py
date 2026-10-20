"""Registro estruturado de observabilidade e auditoria (JSONL)."""
import json
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path("logs/app.jsonl")


def log_event(
    trace_id: str,
    event: str,
    question: str | None = None,
    urgency: str | None = None,
    confidence: float | None = None,
    retrieved_sources: list[str] | None = None,
    context_tokens: int | None = None,
    action_proposed: str | None = None,
    action_executed: bool = False,
    latency_ms: int = 0,
    error: str | None = None,
) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": trace_id,
        "event": event,
        "urgency": urgency,
        "classifier_confidence": round(confidence, 4) if confidence is not None else None,
        "retrieved_sources": retrieved_sources or [],
        "context_tokens": context_tokens,
        "action_proposed": action_proposed,
        "action_executed": action_executed,
        "latency_ms": latency_ms,
    }

    if error:
        record["error"] = error

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

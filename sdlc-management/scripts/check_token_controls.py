#!/usr/bin/env python3
"""Read-only native Claude token-control preflight. Never reads credentials/content."""
import argparse
import json
from pathlib import Path

WINDOW = 250000
PERCENT = 80

def check_settings(settings):
    env = settings.get("env", {})
    errors = []
    if str(env.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW")) != str(WINDOW):
        errors.append("native compact window must be 250000")
    if str(env.get("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE")) != str(PERCENT):
        errors.append("native compact trigger must be 80 percent (200000 tokens)")
    for key in ("DISABLE_COMPACT", "DISABLE_AUTO_COMPACT"):
        if str(env.get(key, "")).lower() in ("1", "true", "yes"):
            errors.append(key + " disables required compaction")
    for model, opts in settings.get("modelSettings", {}).items():
        if opts.get("autoCompactWindow", WINDOW) > WINDOW:
            errors.append(model + " overrides the compact window above 250000")
    return errors

def latest_usage(path):
    # Bounded reverse read: no whole-session rescan; only metadata is returned.
    with Path(path).open("rb") as f:
        f.seek(0, 2)
        end = f.tell()
        size = min(end, 8 * 1024 * 1024)
        f.seek(end - size)
        data = f.read(size)
    lines = data.splitlines()
    if end > size:
        lines = lines[1:]
    for line in reversed(lines):
        try:
            row = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            continue
        if row.get("type") != "assistant":
            continue
        usage = row.get("message", {}).get("usage")
        if usage is None:
            continue
        if not isinstance(usage, dict):
            raise ValueError("unsupported request usage telemetry")
        keys = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
        available = [usage[k] for k in keys if type(usage.get(k)) is int and usage[k] >= 0]
        # Missing counters prevent verification, but cannot erase an observed
        # lower bound that already crosses the hard ceiling.
        return {"input_context": sum(available), "context_complete": len(available) == len(keys),
                "effort": row.get("effort"), "timestamp": row.get("timestamp"),
                "model": row.get("message", {}).get("model")}
    raise ValueError("no usage telemetry in bounded transcript tail")

def inspect(settings, telemetry=None, expected_effort=None, telemetry_problem=None):
    errors = check_settings(settings)
    unverified = []
    result = {"errors": errors, "telemetry": telemetry, "unverified": unverified}
    if telemetry_problem:
        unverified.append(telemetry_problem)
    if telemetry is not None:
        if not telemetry.get("context_complete", True):
            unverified.append("incomplete request usage; input_context is an observed lower bound")
        if telemetry["input_context"] >= WINDOW:
            errors.append("context ceiling reached: compact or checkpoint/handoff before ordinary work")
        if expected_effort:
            if telemetry.get("effort") is None:
                unverified.append("effective effort metadata is unavailable")
            elif telemetry["effort"] != expected_effort:
                errors.append("effective effort does not match the recorded role/override")
        result["checkpoint_due"] = telemetry["input_context"] >= WINDOW * PERCENT // 100
    elif expected_effort and not telemetry_problem:
        unverified.append("last-request usage and effective effort require a transcript")
    result["blocked"] = bool(errors)
    result["ok"] = not errors and not unverified
    result["status"] = ("blocked" if errors else "unverified" if unverified else
                        "verified" if telemetry is not None else "static-only")
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--settings", required=True, type=Path,
                   help="merged effective settings snapshot, or project file for static check only")
    p.add_argument("--transcript", type=Path)
    p.add_argument("--expected-effort", choices=["low", "medium", "high", "xhigh", "max"])
    args = p.parse_args()
    try:
        settings = json.loads(args.settings.read_text())
        telemetry, problem = None, None
        if args.transcript:
            try:
                telemetry = latest_usage(args.transcript)
            except (OSError, ValueError, TypeError) as exc:
                problem = str(exc)
        result = inspect(settings, telemetry, args.expected_effort, problem)
        result["scope"] = ("settings-and-last-request" if telemetry else
                           "telemetry-unverified" if problem or args.expected_effort else "static-settings-only")
    except (OSError, ValueError, TypeError) as exc:
        result = {"ok": False, "blocked": True, "status": "blocked",
                  "errors": [str(exc)], "unverified": [], "scope": "settings-unverified"}
    print(json.dumps(result, sort_keys=True))
    return 1 if result["blocked"] else 0 if result["ok"] else 2

if __name__ == "__main__":
    raise SystemExit(main())

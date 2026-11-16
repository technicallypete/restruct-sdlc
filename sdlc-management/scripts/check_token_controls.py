#!/usr/bin/env python3
"""Read-only native Claude token-control preflight. Never reads credentials/content."""
import argparse
import json
from pathlib import Path

WINDOW = 250000
PERCENT = 80
CHECKPOINT = 200000

def check_settings(settings, expected_percent=PERCENT, expected_window=WINDOW):
    if expected_percent not in (80, 90):
        raise ValueError("expected compact percentage must be an approved 80 or 90")
    if expected_window not in (250000, 275000):
        raise ValueError("expected compact window must be an approved 250000 or 275000")
    env = settings.get("env", {})
    errors = []
    if str(env.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW")) != str(expected_window):
        errors.append(f"native compact window must be {expected_window}")
    if str(env.get("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE")) != str(expected_percent):
        errors.append(f"native compact trigger must be {expected_percent} percent ({expected_window * expected_percent // 100} nominal tokens)")
    for key in ("DISABLE_COMPACT", "DISABLE_AUTO_COMPACT"):
        if str(env.get(key, "")).lower() in ("1", "true", "yes"):
            errors.append(key + " disables required compaction")
    for model, opts in settings.get("modelSettings", {}).items():
        if opts.get("autoCompactWindow", expected_window) > expected_window:
            errors.append(model + f" overrides the compact window above {expected_window}")
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

def inspect(settings, telemetry=None, expected_effort=None, telemetry_problem=None, expected_percent=PERCENT, expected_window=WINDOW):
    errors = check_settings(settings, expected_percent, expected_window)
    unverified = []
    result = {"errors": errors, "telemetry": telemetry, "unverified": unverified}
    if telemetry_problem:
        unverified.append(telemetry_problem)
    if telemetry is not None:
        if not telemetry.get("context_complete", True):
            unverified.append("incomplete request usage; input_context is an observed lower bound")
        if telemetry["input_context"] >= expected_window:
            errors.append("context ceiling reached: compact or checkpoint/handoff before ordinary work")
        if expected_effort:
            if telemetry.get("effort") is None:
                unverified.append("effective effort metadata is unavailable")
            elif telemetry["effort"] != expected_effort:
                errors.append("effective effort does not match the recorded role/override")
        result["checkpoint_due"] = telemetry["input_context"] >= CHECKPOINT
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
    p.add_argument("--expected-percent", type=int, choices=[80, 90], default=PERCENT,
                   help="recorded approved percentage; default 80, explicit owner-selected 90 supported")
    p.add_argument("--expected-window", type=int, choices=[250000, 275000], default=WINDOW,
                   help="recorded approved window/ceiling; default 250000")
    args = p.parse_args()
    try:
        settings = json.loads(args.settings.read_text())
        telemetry, problem = None, None
        if args.transcript:
            try:
                telemetry = latest_usage(args.transcript)
            except (OSError, ValueError, TypeError) as exc:
                problem = str(exc)
        result = inspect(settings, telemetry, args.expected_effort, problem, args.expected_percent, args.expected_window)
        result["scope"] = ("settings-and-last-request" if telemetry else
                           "telemetry-unverified" if problem or args.expected_effort else "static-settings-only")
    except (OSError, ValueError, TypeError) as exc:
        result = {"ok": False, "blocked": True, "status": "blocked",
                  "errors": [str(exc)], "unverified": [], "scope": "settings-unverified"}
    print(json.dumps(result, sort_keys=True))
    return 1 if result["blocked"] else 0 if result["ok"] else 2

if __name__ == "__main__":
    raise SystemExit(main())

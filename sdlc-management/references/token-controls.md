# Native context controls and dispatch acceptance

The coordinator and supervisor own this gate, including every worker/continuation.
Written thresholds alone are insufficient. Configure native early compaction and
verify actual loading, role effort and request metadata. Do not infer enforcement
from a brief, a co-author trailer or a quota percentage.

## Native configuration

Merge (never overwrite unrelated settings) into shared `.claude/settings.json`:

```json
{"env":{"CLAUDE_CODE_AUTO_COMPACT_WINDOW":"200000","CLAUDE_AUTOCOMPACT_PCT_OVERRIDE":"75"}}
```

This targets native auto-compaction around150k, including subagents, with200k the
ordinary-work stop threshold. Respect smaller native limits. Audit higher-priority
settings, per-model `autoCompactWindow`, inherited environment and disabled
compaction. A project-file PASS alone is only a static check. Native limits are
not a precise spending cap: a large response may overshoot; inspect after large
reads and before another expensive step. Do not expose credentials while checking.

Use `scripts/check_token_controls.py --settings EFFECTIVE_SETTINGS.json
--transcript EXACT_WORKER.jsonl --expected-effort ROLE_LEVEL` at first available
worker usage, before continuation/expensive correction dispatch, at handback and
before phase acceptance. The settings snapshot must reflect actual precedence,
not be presented as effective merely because it is the committed file. The helper
checks the last request, not accumulated session totals, and includes fresh plus
cache-creation plus cache-read input. Output/reasoning and account quota are separate.
It reads a bounded metadata tail; missing/unsupported data is UNVERIFIED, never PASS.

At150k checkpoint unique work and compact at a safe boundary. At200k stop ordinary
work: preserve source and use supported compaction or an authorized safe handoff
before proceeding. Do not relaunch duplicate workers, discard active children,
rebind frozen tests, kill running validation or block necessary cleanup merely to
meet a number. A temporarily oversized in-flight call needs immediate recovery;
repeated operation beyond the limit is a gate failure. If native compaction is
unavailable, checkpoint and return control rather than consuming unbounded context.

Effort is role-specific: record the accepted model/effort and any existing explicit
exception, then compare actual metadata. Test-correction/escalation policies can
legitimately require xhigh; a generic high default must not erase them. Unknown or
mismatched settings block new ordinary dispatch until reconciled, not native recovery.

Record compact metrics and configuration/loading evidence in the existing dispatch/
Result inventory, no separate tracking service or polling agent. Do not accept a
phase or dispatch successors while its context/effort exception is unowned. The
supervisor checks this gate at the same event; it is not solely implementer attestation.
Current sessions/worktrees do not automatically inherit a new committed setting:
use supported loading/refresh and first-call verification, preserving permissions.

## Rework and scope controls

Use bounded verified packets and source deltas. Keep one existing lane owner for
consolidated corrections where safe. Before submission reconcile every named
required test with an actual assertion and outcome; NOT PROVEN, fallback fixtures
and skipped checks are not passes. At two review correction loops on one checkpoint,
stop further speculative dispatch and perform a compact root-cause/remaining-scope
fit review under the existing budget; no new process or owner approval if within
existing authority. Required correctness/security checks are never waived to save quota.

## Verification and limits

Run `python3 -m unittest discover -s sdlc-management/scripts -p test_token_controls.py`.
Test boundaries, missing telemetry, compaction reset, role overrides and disabled/
widened config. A static check proves configuration, not live activation. Verify
first-call native metadata after adoption and report any loader limitation. There
is no guarantee on provider quota percentages, cache billing or the size of one
in-flight model/tool response.

Primary native interface references: [environment variables](https://code.claude.com/docs/en/env-vars)
and [settings precedence](https://code.claude.com/docs/en/settings).

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

## Event-driven worker progress stop — no polling

Install the tested `scripts/worker_progress_guard.py` as the identical project
`.claude/hooks/worker_progress_guard.py`, and merge the hooks from
[the native hook configuration](../templates/root/claude-worker-progress-hooks.json) preserving existing settings.
Requires current native hook support and Python3/fcntl (Linux/WSL); an unsupported
host is UNVERIFIED, not permission to silently disable the gate. `onFailure:block`
prevents a missing/crashed guard from silently allowing worker actions.

Native tool-batch callbacks stop a worker before its next model request after40
tool calls without an observed successful Write/Edit/NotebookEdit. A compaction
without such an artifact latches the same stop for the next tool boundary because
PostCompact itself cannot stop native processing. PermissionDenied and recognized
native refusal text also latch a stop; no retry flag is emitted. PreToolUse retains
the latch, while allowing native SubagentHandback. Coordinator events are excluded
from worker budgets. No timers, transcript polling, model calls, shell execution,
resource deletion, permission changes or automatic replacement are performed.

The small locked state file beside the native worker transcript stores counters,
recent tool IDs and a hold reason only; no tool contents or secrets. It survives
compaction/repeated callbacks. Coordinator retains it with task evidence and reclaims
it only under normal verified closeout. A hold requires a bounded artifact/obstacle
review and supported recovery, never automatic reset/relaunch. Bash-generated
artifacts may need checkpoint review; the guard deliberately does not guess from
opaque shell commands. An artifact signal is not a correctness or progress guarantee.
Required tests and running processes remain untouched; coordinator owns recovery.

Verify offline transitions, native JSON output, file-backed latch persistence and
configuration integrity before adoption, then require actual loaded hook evidence
at the next already-authorized worker bootstrap. Hooks changed outside native
settings UI may require supported refresh/confirmation. Do not assume hot loading,
launch an unapproved probe agent, or resume a held lane to test installation.
This is a bounded event-driven stop, not a guarantee about all stalls, silent
reasoning between events or provider quota. The supervisor still checks useful
artifacts and required proof at existing handback/acceptance gates.

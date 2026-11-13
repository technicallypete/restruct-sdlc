# Native context controls and dispatch acceptance

Owner correction, 2026-11-13: checkpoint around200k, ceiling250k. This supersedes
the earlier150k/200k thresholds; smaller native limits and no-output stops remain.

The coordinator and supervisor own this gate, including every worker/continuation.
Written thresholds alone are insufficient. Configure native early compaction and
verify actual loading, role effort and request metadata. Do not infer enforcement
from a brief, a co-author trailer or a quota percentage.

## Native configuration

Merge (never overwrite unrelated settings) into shared `.claude/settings.json`:

```json
{"env":{"CLAUDE_CODE_AUTO_COMPACT_WINDOW":"250000","CLAUDE_AUTOCOMPACT_PCT_OVERRIDE":"80"}}
```

This targets native auto-compaction around200k, including subagents, with250k the
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

At200k checkpoint unique work and compact at a safe boundary. At250k stop ordinary
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

At30 tool calls without an observed successful Write/Edit/NotebookEdit, the
native tool-batch hook injects one checkpoint request into the worker's next
normal model request. The coordinator requests a brief checkpoint at that event:
resolved facts, precise blocker and next concrete edit/deliverable. The worker
returns it through the existing communication/handback path; no timer, poll,
monitor agent or hook-generated model/message call is added. Native
[`PostToolBatch.additionalContext`](https://code.claude.com/docs/en/hooks#posttoolbatch-decision-control)
is the reminder channel, not an acknowledgment or proof of live loading.

A status/checkpoint reply, message or repeated callback never resets the counter.
At40 calls the existing hard pause remains if there is still no observed artifact;
a justified research/design outcome needs bounded coordinator/supervisor review,
not a worker-granted extension. For planners/reviewers, a meaningful findings or
draft artifact is appropriate; repeated still-reading reports are not progress.
A Write/Edit signal alone cannot establish usefulness or acceptance. A completed
artifact starts a new no-artifact stretch and permits a new30-call reminder.
If a single parallel batch reaches40, the hard stop takes precedence; it does not
grant another model turn merely to deliver the earlier reminder.

Native tool-batch callbacks stop a worker before its next model request after40
tool calls without an observed successful Write/Edit/NotebookEdit. A compaction
without such an artifact latches the same stop for the next tool boundary because
PostCompact itself cannot stop native processing. PermissionDenied and recognized
native refusal text also latch a stop; no retry flag is emitted. PreToolUse retains
the latch, while allowing native SubagentHandback. Coordinator events are excluded
from worker budgets. No timers, transcript polling, model calls, shell execution,
resource deletion, permission changes or automatic replacement are performed.

The small locked state file beside the native worker transcript stores counters,
recent tool IDs, checkpoint flags and a hold reason only; no tool contents or secrets. It survives
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

### Worker identity and safe rollout

Native callbacks may supply the parent transcript even for a worker. Resolve the
native agent ID to its existing `SESSION/subagents/agent-ID.jsonl`; direct child
callbacks must match that same ID/session. Never key worker counters to the parent
transcript. Missing, mismatched, traversing or symlinked identities stop verification.
Distinct workers have distinct locked state; parent/child callbacks for one worker
share it. A legacy shared state must not silently become a fresh allowance.

Pin the prior hook for an already-running worker until its terminal handback. At
that boundary preserve its state/refusal evidence and close its ownership before
rebinding native hooks to the corrected script. Do not resume a held worker through
a new namespace, remove its hold, or overwrite live bound hook bytes to install
this fix. A native refusal of recovery remains a refusal; the supervisor owns the
next supported disposition, with owner approval only where genuinely required.

## Dispatch readiness and proof completeness

Use [the delivery checker](../scripts/check_delivery.py) on the existing private
dispatch/handback data; no committed per-worker document or tracking service.
The coordinator prepares one bounded objective, source commit, role/phase, exact
exclusive writable files, an empty unresolved-dependency list and named required
cases with observable expectations. Resolve fixture/contract design before writing
dispatch; a worker blocked by an unresolved design returns that precise obstacle
within the existing progress budget. The supervisor checks the required-case list
against the canonical AC/Spec/Plan, rather than trusting a worker-selected subset.

Run `python3 -B scripts/check_delivery.py --dispatch PRIVATE.json` before dispatch.
The JSON keys are `objective`, `source` (40-hex commit), `role`, `phase`,
`writable_paths` (exact relative files), `unresolved` (empty array) and
`required_cases` (objects with `id` and `expected`). Use resolved existing paths and
fixture facts in the private context packet; do not commission another worker to
rediscover facts already established. A genuinely new design obstacle returns for
bounded disposition, not speculative expansion or repeated full-source reads.

Before submitting a checkpoint as passing, add `--handback PRIVATE.json --repo
CHECKOUT --evidence-root PRIVATE_EVIDENCE`. Handback keys: `source` (actual HEAD),
`dispatch_sha256` (SHA-256 of sorted compact JSON dispatch), `outputs` (objects with
`path`, `sha256`) and `cases` (one object per required ID). Each case records `id`,
`status` (`passed`, `failed`, `not_run`, `not_proven`). A passed case also supplies
an executable `selector` plus `assertion` and `evidence`, each with root-relative
`path`, exact file `sha256` and an exact `excerpt` from that file. Evidence roots
must not contain secrets. Hashes bind evidence, not its correctness.

The checker rejects missing/duplicate/unknown cases, unowned declared outputs,
source/dispatch mismatches, missing/changed files and absent excerpts. Non-passes
remain incomplete, never an aggregate PASS. Writer-only handbacks may be incomplete:
the coordinator runs the authorized selectors and fills actual evidence before
checkpoint submission; no extra worker test authority is granted. Exit0 proves
completeness/bindings only. The coordinator and supervisor still inspect actual
assertions, outcomes, provenance and the complete Git diff (including undeclared
changes); arbitrary log text or a case name alone proves no behavior. Genuine
coverage discoveries amend the existing records; never shrink a bound checklist
silently to get a green result. Run the focused tests in `test_delivery.py` when
changing this checker; no application suite is needed for its adoption.

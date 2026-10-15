<!-- Bundled fallback adapted from the originating repository's docs/agents/CLAUDE-SESSION-HANDOFF.md. Prefer the target repository runbook when present. Relative repository paths below refer to the target checkout. -->

# Codex ↔ Claude Code session handoffs

Operational note, verified locally on 2026-10-06 with Claude Code 2.1.290/2.1.291 and reverified on 2026-10-10 with 2.1.296 on Linux/WSL. Codex uses shell tools to discover, inspect and message Claude Code sessions. Codex's own collaboration tools address Codex agents; they do not address an existing Claude Code session.

This runbook records the existing handoff mechanism, not a new execution framework. It does not authorize extra implementation, permission changes, session restarts, commits or external actions. Follow the target repository's AGENTS.md and the current task's approved scope/budget/binding.

## Find the intended session

From the repository root:

```sh
claude agents --json --all --cwd "$PWD"
```

Match session name, full session UUID and checkout path. Several sessions may belong to this project; some are stopped/completed or work in separate worktrees. Do not pick the first entry or reuse a remembered PID. The short background ID is useful for CLI commands; the full UUID identifies the conversation.

Inspect the chosen registration at `~/.claude/sessions/<pid>.json`. Relevant fields include `pid`, `sessionId`, `cwd`, `name`, `status`, `version`, `peerProtocol`, `procStart` and `messagingSocketPath`. After a restart, rediscover them; the process/socket may change while the conversation UUID is retained.

Check `kind` in the CLI listing. A stopped background entry and a live
interactive entry can share the same UUID; select the verified live process.
`claude attach` and `claude logs` operate on background sessions, not an
interactive instance already running in another terminal. For interactive
sessions, use the verified inbox or the owner's existing terminal. Do not
start a duplicate resume. Missing host process visibility (for example, a
restricted PID namespace) prevents verification and does not prove shutdown.

## 2026-10-10 compatibility verification

Installed CLI 2.1.296 still has no native `agents send` command. Its registered
protocol-1 inbox accepted an authenticated, peer-verified handoff; transcript
replay and the recipient acknowledgment were verified. This supports the same
narrow helper protocol, not a claim of a new public messaging API. Keep
unverified versions blocked. Claude-to-Claude messaging uses the CLI's native
`ListAgents`/`SendMessage` tools; this inbox procedure is for Codex → Claude.

## Check status and progress

Try `claude logs <background-id>` for recent output. If the local daemon/log bridge fails, read the session's JSONL transcript under `~/.claude/projects/<encoded-checkout>/<session-uuid>.jsonl`. Find it by exact UUID and confirm its checkout; do not guess the directory encoding. Subagent transcripts live under `<session-uuid>/subagents/`.

Read a bounded tail and extract assistant text, timestamps and tool descriptions. Avoid printing raw tool inputs/results, environment dumps, credential files or entire transcripts. Combine session status with actual test/run logs and Result existence; `busy` or an updated transcript alone does not prove a gate passed. A monitor expiry is not a test failure or completion signal.

Prefer user-requested checks or checks at handoffs. Continuous polling is unnecessary. If the session is running tests, inspect progress without launching competing stacks or editing its checkout.

### Waiting-state prompt check

`waiting` with no unanswered transcript question/tool does not establish absence
of a native prompt. Inspect the verified existing background terminal with
`claude attach <id>` before reporting no open questions; interactive sessions need
their existing terminal. If inspection is unavailable, report prompt state as
unverified. Inbox messages can queue behind dialogs. Use the supported native
procedure to answer only within recorded owner authority, verify the response,
then detach without stopping the worker. No automatic approval, permission bypass
or settings change is implied.

## Send instructions to a running session

In the locally verified CLI, `claude agents` discovers/manages sessions but has no documented `send` subcommand. We used Claude Code's authenticated local Unix-socket inbox instead of starting another copy of the running conversation.

**This inbox is an internal, version-specific interface.** Before using it after a Claude upgrade, verify the current local registration/protocol and installed CLI implementation. Do not assume the wire format, key layout or socket namespace is a stable public API. If it is unavailable or incompatible, use `claude attach <id>` for a background session or the owner's existing interactive terminal, or report that the handoff could not be delivered. Do not write a fabricated user entry into the transcript or job files.

Verified protocol 1 on this host:

1. Connect to the target registration's `messagingSocketPath`, normally `/run/user/<uid>/cc-socks/<pid>.sock` (another local socket location may be published).
2. Derive the local key filename as `<pid>.<sha256(canonical-socket-path)>.key` under `~/.claude/sessions/`. Read its `peerToken` directly into memory.
3. Send newline-delimited JSON: first `{"type":"auth","token":...}`, then a `type: user` frame with the exact target `session_id` and string `message.content`.
4. Use `priority: next` for routine supervisor handoffs so instructions are queued without requesting immediate interruption. Include a unique `uuid` and identify the sender as `codex-supervisor`; that label does not replace the socket authentication or repository approval record.

The following example sends one text file without putting the token into a shell argument or output. Replace the PID/UUID/path after discovery. It requires local Python only for the supervisor handoff; it does not change the application's Docker-first runtime policy.

```sh
python3 - TARGET_PID TARGET_SESSION_UUID /absolute/outside-checkout/handoff.txt <<'PY'
from pathlib import Path
import hashlib
import json
import os
import socket
import sys
import time
import uuid

pid = int(sys.argv[1])
expected_session = sys.argv[2]
content = Path(sys.argv[3]).read_text()
assert content.strip(), "Empty handoff"
registry = Path.home() / ".claude" / "sessions"
registration = json.loads((registry / f"{pid}.json").read_text())
assert registration["pid"] == pid
assert registration["sessionId"] == expected_session
assert registration["peerProtocol"] == 1, "Reverify changed protocol"
os.kill(pid, 0)  # Existence check only; sends no signal.
linux_start = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[19]
assert str(registration["procStart"]) == linux_start, "Stale/reused PID"
address = registration["messagingSocketPath"]
assert address.startswith("/") and address.endswith(".sock")
assert os.path.realpath(address) == address, "Reverify noncanonical socket path"
key_path = registry / f"{pid}.{hashlib.sha256(address.encode()).hexdigest()}.key"
token = json.loads(key_path.read_text())["peerToken"]
frame = {
    "type": "user",
    "session_id": expected_session,
    "uuid": str(uuid.uuid4()),
    "from": "codex-supervisor",
    "priority": "next",
    "message": {"role": "user", "content": content},
}
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
    client.settimeout(5)
    client.connect(address)
    client.sendall((json.dumps({"type": "auth", "token": token}) + "\n"
                    + json.dumps(frame) + "\n").encode())
    time.sleep(0.4)  # Allow consumption; this is not an acknowledgment.
print("Sent to the local inbox; Claude acknowledgment is still required.")
PY
```

Never print/copy/commit the key or token. Do not include them in handoff files, task prompts, logs or evidence. They authenticate the local inbox and are distinct from Git-hosting/provider credentials. Use this only for the user's authorized local session communication; never redirect the secret or handoff to a remote socket/service.

## Confirm receipt and dispatch

A successful socket write proves only that bytes were sent. It does **not** prove acceptance into the queue, model consumption, subagent creation or task completion. Look for the handoff's user replay or Claude acknowledgment in the target transcript. Until then, report “sent; acknowledgment pending.” Do not repeatedly resend just because acknowledgment is delayed during a tool/test run; avoid duplicate tasks.

For delegation, require Claude to report the child ID, configured effort, isolated checkout and output path. Asking for `xhigh` in text is not evidence that it was configured. If Claude dispatches a separate CLI agent, `--effort xhigh` makes the requested level explicit; use the current CLI's supported delegation interface. Only say the child started after verifying dispatch.

Completion requires the promised repository artifact, attributable validation where applicable, and a handback. A finished background process is not Codex Plan approval or implementation ACCEPT.

## What a supervisor handoff contains

- Goal and exact Goal/Spec/Plan/ADR paths/revisions; baseline commit or approved snapshot/digest where execution is authorized.
- Whether the task is read-only research, planning, approved implementation or a bounded correction; exact allowed writes/output path.
- Requested effort, delegation boundary, shared budget/checkpoint, required validation and stop conditions.
- Protection of the active checkout, bound inputs, snapshots and developer/Docker resources; separate checkout for unrelated parallel planning.
- Required artifact save/return and acknowledgment; no implied commit/push/hosted authorization.

Write a new Plan into its goal-specific repository path in the designated planning checkout. Do not leave it only in Claude's internal Plan mode directory or chat. A side checkout does not bypass scope/approval. Superseding architecture/progress documents in main are not silently copied into an active execution checkout; reconcile after the accepted phase transition with a fresh binding.

If a stopped background session must restart, use `claude attach <short-id>` or `claude respawn <short-id>`, which keep the session UUID, and only when authorized. Never use `--resume … --bg` or a name-based resume: either may start a copy, causing duplicate work. Do not resume an already-running session as a messaging shortcut. Do not stop/restart a live session or change permission mode merely to send a handoff.

## Preferred coordinator, creation and closeout

The skill's helper can pin one verified live session as the repository's preferred
coordinator in private machine-local state (never in Git; no PID, socket, token or
transcript data). Without `--session`, `check` and `send` route only to a pin whose
status is `pinned-live-verified`; explicit `--session` routing is unchanged.
Discovery combines the registry with the CLI listing and reports duplicates; an
incomplete view is `unknown`, never "no coordinator". Names never identify a target.

Creating a new coordinator is a documented operator procedure, not a helper command:
run the read-only `status --creation-check` gate immediately before creating, and
create only when it reports no reusable live or stopped coordinator, no unknown or
ambiguous candidate, a verified CLI version and a bound, supervisor-verified owner
creation authority. On any refusal, reuse, restart, select or escalate.

Delivery logs are append-only history until a task's terminal disposition is
verified by the supervisor or owner. Then `compact` archives that task's whole
delivery groups to a private archive before pruning them from the live log
(dry-run first; apply bound to the reviewed selection, only from the main checkout
in a quiet maintenance window, refusing while any other helper invocation runs or
holds the log). Preserve any worktree-local delivery log in the archive before
removing that worktree. See the skill for the exact commands and refusals.


## Coordinator milestone observer

The companion `watch.py` polls the verified coordinator's assistant transcript at a 30-second default. It reports
failures, review readiness, blockers, questions and explicit decision/approval requests, waiting and completion.
Absent, expected or explicitly resolved issues are filtered. Detection is bounded text matching, not AI inference
or direct CI polling; notices carry no approval or task authority. Incoming handoffs, echoed notices, sidechains
and repository edits are excluded as sources.

After explicit verified coordinator/supervisor bindings, `start` begins at the current transcript tail, avoiding
historical backlog even after a prior activation. After stopping, use `start --resume` only for deliberate catch-up
from the saved cursor. Both retain deduplication and advisory history; unresolved delivery uncertainty blocks fresh
activation, and an already-running observer's cursor is never reset. The standalone companion is opt-in; adopted
repositories may default-enable it after verified bindings. See [the skill](../SKILL.md) for commands, private-state
safety, version support, size advisories and suspension/recovery rules.

## Model-aware effort override — 2026-10-15

Default to Fable 5.1 high for planning and test corrections, including failure
diagnosis and corrective test/fix work; use xhigh selectively for especially
hard work. Default to Opus 5.5 high for implementation, routine test execution
and coordination. If the owner selects Opus 5.5 for planning or test
corrections/diagnosis, use xhigh; routine implementation, test execution and
coordination stay high. This overrides generic role-effort defaults for those
models/phases. Honor owner choices, verify actual settings or report unknown,
and apply only at the next phase/safe boundary without restarting completed work,
interrupting a batch or resetting budgets. Prose does not configure the runtime.


## Fable weekly-limit fallback — owner direction, 2026-10-15

When Fable's weekly allowance is confirmed exhausted, automatically use Opus 5.5
**xhigh for planning and test-failure diagnosis/corrections** until Fable resets.
Opus implementation, ordinary test execution/reporting and coordination remain
**high**. This standing fallback needs no repeat owner approval; honor an explicit
owner override. Record the limit, fallback model/effort and actual setting (or
unknown) in the existing Result/dispatch record. A generic tool error is not
proof of a model limit.

Use supported controls at the next safe boundary, preserving the existing task,
artifacts, checkout, bindings, reviews and attempt count. Do not interrupt a
running validation batch, redo completed work, reset budgets or weaken gates.
If native switching is unavailable or refused, report the blocker once; do not
bypass permissions. Once Fable's allowance reset is verified, return to its normal
model/effort defaults at the next safe phase boundary, without restarting work or
repeatedly probing the allowance. This is model selection only, not scope,
execution-release or budget-extension authority.


For routine status/handoffs use [concise operational messages](../../sdlc-management/references/coordination.md#concise-operational-messages).
Report changes and actionable waits, reference the existing decision record and
continue authorized next actions; do not repeat settled context or approval prompts.


Observer queue compatibility verified 2026-10-15: Codex CLI 0.160.0 with daemon
0.162.1/0.163.0. Other daemon versions remain fail-closed until verified; preserve
the existing bound sessions, cursor, deduplication and permission boundaries.

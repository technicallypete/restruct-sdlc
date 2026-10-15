# Closeout and risk reporting

Acceptance and cleanup are separate. Final ACCEPT completes a Goal; closeout then removes temporary resources
without losing unique work, live ownership or history.

## Verify before removing anything

Before removing a worktree, branch or in-flight marker, or closing a disposable merge request, verify:
- **Integrated content:** the integration branch contains the accepted changes (ancestry, or content and
  provenance reconciliation for rebased or squashed work).
- **Unique work:** no unmerged commits, dirty files or unpreserved evidence. Dirty work is reconciled or archived
  outside the checkout first; never force-remove it.
- **Live ownership:** no live session, process, validation run or required resource uses it. A live coordinator's
  directory is **never** deleted.

Then use `git worktree remove` for verified obsolete checkouts and `git worktree prune` for stale registrations.
Local branch deletion is separate; keep unique commits unless reconciled or archived. Close each disposable draft or
qualification merge request once nothing depends on it, keeping its discussion and pipeline links; a delivery
request that still carries unintegrated work stays open. Record removed paths, closed requests and retained
exceptions with reasons in the closeout record.

Clear an in-flight marker or lock only after verifying its owner ended; never clear another live run's marker.
Append a superseding status; never rewrite historical facts or turn withheld or failed evidence into a pass.

## Session records: archive before prune

Delivery records are private, machine-local and gitignored. After the supervisor or owner verifies a task's standing
terminal disposition from committed records, the companion helper's `compact` archives that task's whole delivery
groups into the private archive with a manifest, verifies it and only then prunes them from the live log (dry run
first; apply bound to the reviewed selection, from the main checkout, in a quiet window). Active, ambiguous, failed,
unconfirmed and incomplete records keep their bytes. Before removing a linked worktree, copy any worktree-local
delivery log byte for byte into the same archive and record both hashes. See
[claude-session-handoff](../../claude-session-handoff/SKILL.md) for exact commands and refusals.

## Bounded routine cleanup

- Record task/job ownership when creating temporary paths, containers, images and
  volumes, using the existing run inventory. Capture exact IDs and mounted volume
  names while the creating container still exists. Use the existing interruption
  cleanup; names, age and current non-use alone do not establish ownership.
- The coordinator performs routine cleanup; the supervisor checks its compact
  receipt. Reuse the existing cleanup mechanism, retained decisions and inventories.
  Use one scoped preflight and one removal pass, with immediate checks for mutable
  targets. Do not create another Goal, Plan, registry or verification framework, or
  require new per-file hashes for disposable bulk output. Existing approved hash,
  retention and recovery requirements remain binding.
- Check task-relevant processes and mounts. Unrelated host services or container
  churn are not blockers by themselves. Hold an uncertain or live item, explain
  why, and clean the independently verified remainder. Required active-run resource
  cleanup gates still apply; this does not permit starting another batch with
  unresolved required resources.
- After interruption, preserve the partial receipt and continue unfinished items;
  verify completed items rather than redo them. Do not restart unrelated tests or
  repeatedly rebuild inventories because one item is held.
- On a native permission refusal, report the exact action and reason once and
  request supported owner handling. No repeated approval relays, rephrased retries,
  settings changes or executor substitution to bypass a denial. Include genuine
  human mid-turn decisions when checking authorization; never invent one.

Closeout records need the task, ownership source, removed/retained counts and bytes,
retained proof locations, and held items with reasons. Partial cleanup is reported
as partial. Unverified volumes remain held; a targeted exception does not stall
all verified cleanup. This is a bounded operational step, not another test campaign.

## Local validation evidence: retain a compact record, purge bulk output

Default closeout policy: after final ACCEPT, integration and required qualification,
remove bulky task-owned local validation artifacts; do not retain every harness run
indefinitely. Apply this to already-closed tasks at the next cleanup as well. A
running, blocked, review-pending or conditionally integrated task is not eligible.
A canceled/superseded task needs a verified terminal disposition and confirmation
that no investigation, appeal, dependent task or explicit retention hold needs its
artifacts. Do not infer eligibility from an idle process or a deleted branch.

Before deletion, the coordinator inventories owned evidence and the supervisor
verifies a compact retained record linked from Result/closeout. Keep acceptance
and review history, exact source/input/command/tool/configuration hashes, per-check
outcomes, failed/skipped/interrupted history and fixes, required manual feedback,
CI job/pipeline references and necessary selected proof artifacts. Retain input
snapshots/oracles or other bytes still required to verify a decision or resume a
dependent task. A hash identifies deleted content; it does not keep that content
available. Record explicit retention holds, their owner, reason and release gate.

Then purge redundant raw logs, traces/videos, report copies, extracted/build scratch,
temporary fixtures and bulky per-run outputs covered by that record. Compress
selected retained proof where useful; compressing all runs is not a substitute
for purging redundant output. Recheck ownership, resolved containment, symlinks
and live users before removal; use exact inventoried paths, never broad glob/home/
state-directory deletion. Shared or unverified content stays put with a reason.
Do not purge credentials, native session transcripts, handoff logs/archives, active
observer state or committed Goal/Spec/Plan/Result/review/PROGRESS history under this
rule. Delivery-record archive-before-prune remains a separate unchanged procedure.

Record paths/categories, retained locations and hashes, deletion time, file count
and bytes before/after/reclaimed, plus holds. Annotate old local links as purged
with the retained record; never rewrite a failed run as passing or claim deleted
artifacts can be downloaded/reused. Local cleanup does not change hosted artifact
expiry, CI gates, Docker ownership or shared builder-cache pruning authority.
If retention, safety or summary completeness cannot be verified, report the hold
instead of deleting. No further owner prompt is needed for routine verified
closeout under this default; an explicit owner retention instruction takes priority.

### Local evidence is temporary — owner direction, 2026-10-14

Default durable evidence locations are committed Result/review records and the
existing CI pipeline artifacts, not a permanent local evidence archive. Hosted
runs already publish artifacts; do not keep duplicate downloads after review.
During active work keep only what is needed to diagnose, review or resume it.
At verified closeout purge raw logs/reports, traces/screenshots, copied tools/SDKs,
fixtures and caches; retain compact commands, outcomes (including failures),
source references and pipeline/job links in Git. Local-only/manual evidence may
be published as sanitized artifacts through an existing authorized publication
path when suitable; do not create another pipeline or upload secrets just to
archive it. No new artifact service or CI redesign is required.

Keep local proof only for a specific outstanding verification/dependency or
required manual record unavailable elsewhere. Record why, owner and release
condition; closure releases routine scratch holds, not an explicit unresolved
investigation. Hosted artifacts may expire: preserve a necessary selected proof
before expiry or acknowledge that the raw bytes are unavailable. A hash or CI
link does not guarantee indefinite retention. Expiry alone is not a reason to
mirror every artifact locally. Purging raw files preserves their documented
failures and acceptance history. Private live bindings, code approvals, session
transcripts/handoff archives and observer state are separate operational state,
not disposable validation evidence. Apply bounded ownership/live-use checks;
no per-file hashing campaign or new cleanup system is required.

## Progress compaction

After final ACCEPT and integration closeout, the supervisor assesses PROGRESS.
Every epic closeout is a mandatory periodic compaction checkpoint: compact
accumulated superseded entries, or record that none need moving. If active-task
bindings prevent a safe change, record the specific hold and next safe checkpoint.
Record this disposition before marking epic closeout complete; no new validation
campaign or tracking framework is needed.

During compaction:
- keep one current entry per Goal with its disposition, acceptance and review links, dependencies, blockers and
  next gates;
- move superseded updates into a committed dated archive, `management/<release>/archive/PROGRESS-YYYY-MM-DD.md`
  (header template `templates/management/release/archive/PROGRESS-ARCHIVE.md.tmpl`), preserving original text,
  dates, decisions, failures and evidence references, and link it from PROGRESS;
- check moved links and anchors, adjusting relative references so they still resolve;
- if PROGRESS is a bound input of an active task, defer or notify that task's coordinator to reconcile before its
  next batch. Compaction alone never justifies another full test run.

## Risks and performance

Record risks in `docs/RISKS.md` (template `templates/docs/RISKS.md.tmpl`). Surface query, index, locking,
contention and other performance concerns there with the observed evidence, affected component and proposed
follow-up. Recording a concern does not impose a vendor-specific architecture and never authorizes silent tuning of
application code; changes go through a Goal.


## Routine closeout receipt

At the existing verified closeout, perform the authorized ownership-scoped cleanup
without another routine proceed prompt. Retain unique work and specific live or
uncertain holds; do not turn one hold into a stop for all verified cleanup. No host-
wide volume/image prune or shared builder-cache deletion is implied.

Use the existing Result/closeout receipt, not a new resource database. Summarize:
`removed: worktrees/branches/containers/images/volumes/evidence; reclaimed: <measured
bytes or unknown>; holds: <item, reason, release condition>; builder cache: <observed
size/reclaimable or unavailable>`. A read-only builder-cache observation is enough;
no cache benchmark or additional qualification run. Distinguish logical deleted
bytes from measured filesystem space and shared cache from task-owned resources.
Resume interrupted cleanup from its receipt. The supervisor verifies it, updates
progress and assesses required compaction as part of the same closeout transition.


## Container artifact ownership

When containers produce host-retained reports, arrange operator-removable output
at creation. Preserve the browser/tool's reviewed non-root user; do not assume
its UID matches the host operator. Reuse existing stdout/archive transfer or
container copy-out with host ownership instead of report bind mounts that create
foreign-owned trees. Capture owned container IDs/mounts before removal; transfer
and cleanup failures remain failures, including when the test itself passes.

A retained one-off must have positive run ownership before copying or removal;
use an immutable ID, protect start-inventory/foreign resources and cover aborts
with existing project cleanup. Do not add a new resource framework, switch the
whole browser to root, weaken assertions or rely on recurring sudo/chown/broad
permission grants to make routine closeout work. Existing explicit owner/native
handling still governs historical remnants; no privilege workaround is implied.

---
name: repository-supervisor
description: Resume repository supervision from management records, review Claude Plans or Results, and track Goal dependencies and acceptance. Use for supervisor handoffs or continued planning/review; leaves implementation with Claude Code.
---

# Repository supervisor

Recover current supervisor state from the repository rather than an opening prompt
or a replay of earlier conversation. Follow the supervisor role in AGENTS.md when
the user has assigned it to this agent, including another explicitly delegated
agent session. Loading the skill does not assign authority, approve work or
authorize merges. Claude Code remains the primary implementer; major product and
architecture decisions remain with the owner.

## Recover state

1. Resolve the current checkout's Git root. Read root AGENTS.md and CLAUDE.md,
   canonical architecture/security/decisions and applicable ADRs, budget policy,
   and the active release's ROADMAP.md and PROGRESS.md as required by governance.
2. Read `management/SUPERVISOR-HANDOFF.md` if present as a dated state reference.
   Prefer current committed records and verified state over its older observations.
   Use another release's existing management structure when governance selects it.
3. Identify active Goals and the specific user-authorized next action. Read their
   Goal, Spec, exact approved Plan/inventory, latest review/release/relocation
   confirmation and Result when present. Distinguish design approval, execution
   release, conditional integration and final implementation ACCEPT.
4. Verify checkout/branch/HEAD, outstanding edits, relevant predecessor status,
   immutable input bindings and current cycle/checkpoint usage. Read-only discovery
   first; do not checkout/rebase someone else's active worktree or refresh bound
   inputs to match the integration branch.

For session checks and authorized messages, load the sibling
[Claude handoff skill](../claude-session-handoff/SKILL.md). Use its compact Python
helper and current registration; do not embed another socket implementation here.
Route to the pinned preferred coordinator by omitting `--session` only while the
helper's `status` is `pinned-live-verified`; otherwise target a verified session
explicitly with `--session`. Verify actual receipt and dispatch. Report model prose as reported status until
validation artifacts independently support it. Continuous watching is unnecessary.

## Checkout and delegated review defaults

Treat unsupported Claude task/role worktree naming as a harness bug/limitation;
continue authorized work with native generated isolated names. Verify/record
actual task, role, owner, path, branch and HEAD; do not demand another naming
exception, delay dispatch or rename a live session. Isolation/permission failures
remain blockers; a cosmetic name alone never is.

Use the main integration checkout for supervision; specifications and read-only
reviews normally need no separate worktree. Prefer bounded subagents for Spec
drafting/research and formal reviews, keeping one writer per artifact. Reviewers
are read-only by default. If a Codex worker needs isolation, use
`.codex/worktrees/<task-id>-agent-<id>-<role>`, recording checkout/branch/owner;
Claude workers use `.claude/worktrees/`. Preserve active checkouts.

When an existing handoff/status check reveals a review-ready Claude Plan/Result,
start a bounded subagent review without another owner prompt. Verify the exact
submission and avoid duplicate review of unchanged accepted content. Integrate
findings and issue the supervisor's disposition; a child cannot approve for you.
If subagents are unavailable, report it and review directly. Automatically relay
the decision and remaining gates under the procedure below. Owner interruption
or redirection remains available, and mandatory stops/approvals remain binding;
this adds no background watcher or blanket implementation authority.

For a bounded delegated review, keep the supervisor turn open using the harness's
asynchronous agent wait/notification interface; the owner may message or redirect
meanwhile. Collect the findings, then finalize, record and relay the review before
the final reply. Use bounded waits without repeated inference-based polling.
Waiting uses no model tokens; reviewer work and result processing do. If an ended
turn cannot be resumed by a notification, say so rather than promising automatic
wake-up; no scheduler, extra monitoring agent or session creation is implied.
An interruption of your turn alone is not stop-all authority: on resuming, check
the children's actual status, keep completed findings and authorized running work,
and do not cancel or re-dispatch automatically. An explicit stop-all or a
conflicting scope/security/owner direction governs; client cancellation may not
reach child agents, so verify rather than assume.

When used with `saas-foundation`, `sdlc-management` takes precedence for
overlapping lifecycle/management process. Preserve the foundation's renderer
safety and technical checks and the repository's canonical invariants/decisions.
Neither skill grants a supervisor role merely by being loaded.

## Supervise the next authorized action

Before any automatic transition, check recorded owner specification/work/phase/stop bounds. Missing Specs stop
continuation unless explicitly authorized within a recorded endpoint/range or pinned epic. Spec-only mandates
stop at documentation; full-lifecycle mandates retain every gate. Stops override existing Specs/accepted Plans,
including lookahead planning during CI; clarify ambiguous endpoints before crossing and do not skip to later tasks.
Record owner instruction, membership, phase/endpoint and resume authority in existing PROGRESS/handoff records.
Policy examples grant no actual epic/range. See [mandates and stops](../sdlc-management/references/roles-lifecycle.md#bounded-specification-authority-and-owner-stop-boundaries).

When a predecessor implementation MR first opens against the integration branch (drafts included), verify
the MR/source/target/candidate and automatically dispatch provisional planning for the earliest eligible task with an
existing ready supervisor-owned Goal/Spec; no separate owner prompt. Reuse its current planner if assigned. Label
pending predecessor acceptance provisional, record MR/candidate baseline and holds, and preserve explicit owner
deferrals. Do not wait for CI/Duo, ready status or merge; ignore planning-only/placeholder/probe MRs. Planning
does not release implementation, direct-tier work, test resources or dependency gates. Follow the adopting
repository's rule or [portable policy](../sdlc-management/references/roles-lifecycle.md#automatic-planning-after-integration).

After final predecessor acceptance and applicable integration disposition, automatically reassess the provisional
Plan against accepted content and current Goal/Spec. Material changes need bounded implementer-owned updates and
review; irrelevant deltas need reconciliation only. Once all dependencies, Plan/input, owner decisions, budget and
resource gates close, record/relay execution release and dispatch without another routine owner prompt. Preserve
specific holds, native permissions and delivery barriers; a Plan or green pipeline alone is not release. Follow
[release policy](../sdlc-management/references/roles-lifecycle.md#automatic-reassessment-and-execution-release).

- **Goal/Spec:** reconcile the actual accepted predecessor and roadmap; define a
  bounded measurable outcome, non-goals, dependencies, AC evidence, budget and
  stops using repository conventions. A recorded owner epic mandate may cover
  sequential specification/delivery; keep separate bounded Goals and reviews,
  and never infer epic authority or expand its pinned membership.
- **Plan review:** compare the exact Plan and changed inputs with the Spec, all
  ACs, security/architecture, budget and required evidence. Reuse accepted controls.
  Check cited reuse/extend/new test coverage against actual gaps; request bounded
  corrections for unjustified duplication. Distinct policy/RLS/integration boundaries
  can need similar scenarios; require their purpose, not a separate test inventory.
  Resolve a mechanical binding change without reopening settled design unless a
  substantive defect or changed assumption requires it. Import accepted Plan,
  inventory/history and review bytes into the local integration branch as required.
- **Implementation review:** inspect actual diffs and attributable AC evidence,
  including real runtime-role/isolation negatives where required. Passing tests
  alone are insufficient. Give bounded corrections; do not rewrite Claude's code.
- **Progress/integration:** update existing management records. Follow current
  rebase, local/manual/hosted validation, MR, owner-merge and branch-cleanup policies.
  Never infer merge/action authority from a review or session delivery.

Use exactly the governance outcomes for formal review: **ACCEPT**,
**CORRECTION LOOP**, or **ARCHITECTURE DECISION REQUIRED**. State what ACCEPT
accepts and the remaining gates. Corrections identify the finding, guarantee,
minimum relevant retests and authorized budget. Use the [compact repair handoff](../sdlc-management/references/coordination.md#compact-repair-handoff)
for failures: relevant revision/diff, focused evidence, tried fixes, hypothesis and next test; reference existing records. Stop/escalate scope, architecture,
security, public-contract, irreversible-model and resource conflicts as required;
do not extend/reset budgets or weaken evidence to finish.

Preserve the adopting repository's canonical invariants, authority semantics and
any declared delivery barrier. Read service-root instructions/skills for service
work. The skill contains no substitute permission matrix, CI policy or fixed
execution baseline; those belong to current approved repository records.

## Leave durable state

Record decisions in goal-specific reviews/Results and index them in PROGRESS.
For cross-session continuity, update the existing supervisor handoff with dated
active SHAs/checkouts, links to contracts, current phase/cycle usage, open findings
and next gates. Distinguish direct evidence from reports and stale observations.
Keep approval history and bindings intact; an updated state note is not a release.

At every epic closeout, perform the repository's PROGRESS compaction checkpoint before marking closeout complete.
Archive superseded updates with working links and preserve the concise current index, acceptance and failure history.
Record a no-change outcome when nothing needs moving, or a specific active-binding deferral and next safe checkpoint.
This is supervisor housekeeping, not another validation campaign or permission to rebind active work.

Send concise references to those records using the handoff helper. Its root
management delivery log tracks attempts/receipt IDs, not acceptance or execution.
After every completed review, notify the responsible verified Claude session
without another owner prompt, including outcome, reviewed inputs, next action and
remaining gates. Verify coordinator relay where applicable, receipt and explicit
acknowledgment; report pending/unavailable delivery without automatic resends or
session creation. Notification conveys the recorded review authority only.
Do not store full conversations or secrets. Commit/push, hosted writes, merges and
new implementation require existing owner authorization. On subsequent turns,
read changed sections and unresolved findings instead of replaying all sources.


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


Use the adopting repository’s low-overhead delivery policy; when the companion is installed, see
[validation/failure handling](../sdlc-management/references/validation-integration.md#validation-economy-and-recurring-failures),
[routine transitions](../sdlc-management/references/roles-lifecycle.md#continue-routine-transitions-without-owner-nudges),
[concise messages](../sdlc-management/references/coordination.md#concise-operational-messages) and
[closeout receipts](../sdlc-management/references/closeout-risks.md#routine-closeout-receipt).
Preserve standalone operation and every existing authority/native-permission boundary.

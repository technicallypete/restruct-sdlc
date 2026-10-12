# Roles, artifacts and lifecycle

This reference defines who owns each management artifact, what each artifact contains and how a Goal moves from
proposal to final acceptance. Actor names are parameters (`OWNER_ROLE`, `ARCHITECTURE_AUTHORITY`,
`SUPERVISOR_AGENT`, `IMPLEMENTER_AGENT`); the adopted repository's governance files hold the concrete names.

## Precedence

1. Harness and platform instructions, then explicit owner direction.
2. The adopting repository's canonical governance, architecture and accepted decisions.
3. This skill's references and the instantiated templates.

A skill or template never overrides a higher-priority instruction. A policy change records its scope and its
authorizing actor truthfully; nobody widens their own authority by editing a policy file.

## Ownership matrix

| Artifact or responsibility | Owner | Purpose |
|---|---|---|
| Product and architecture direction | Owner (with the architecture authority) | Canonical decisions; major changes are decided here and never silently by an agent. |
| Roadmap, Goal, Work Spec | Supervisor | Dependency-ordered Goals, bounded outcomes, requirements and acceptance criteria. |
| Plan review, implementation acceptance, progress | Supervisor | Review against scope, architecture, security, budget and every criterion; maintain PROGRESS. |
| Implementation Plan, implementation, tests, Result | Coordinator / implementer | Concrete approach, code, validation and the evidence record. |
| Tactical workers | Coordinator / implementer | Bounded, non-overlapping delegated work; the implementer integrates and validates it. |

Workers, reviewers and subagents never hold owner or supervisor authority. A delegated opinion does not replace
supervisor acceptance or an owner decision.

## Artifacts

All Goal artifacts live under `management/<release>/` with a stable Goal ID (default form `G###`) and a
descriptive stem: `goals/<ID>-<stem>.md`, `specs/<ID>-<stem>-spec.md`, `plans/<ID>-<stem>-plan.md`,
`results/<ID>-<stem>-result.md`, and review records such as `results/<ID>-implementation-codex-review.md`.
IDs are never renumbered or reused. Revisions append dated records or create linked revision files
(`<stem>-plan-r1.md`); prior approvals, failures and evidence are never erased.

**Goal: eleven fields, in this order.** 1. Goal ID and title. 2. Objective. 3. In Scope. 4. Out of Scope.
5. Dependencies. 6. Completion Definition. 7. Execution Policy (including the risk tier). 8. Iteration Budget.
9. Context / Scope Budget. 10. Suggested Subagents / Delegation. 11. Stop / Escalation Conditions.

**Work Spec:** requirements, architecture constraints, security invariants, expected artifacts, acceptance
criteria with verification, required tests and validation, and explicit non-goals. A Spec states what must be
true, not how to code it.

**Plan:** approach; files/modules; schema/migration changes (or none); contracts and public-interface
implications; tests and validation batches; delegation (including a decision not to delegate); sequence; a
mapping of every acceptance criterion to concrete changes and evidence; risks and escalations. Scale detail to
the change and reference accepted controls by path instead of copying them.

**Result:** status (submission is not acceptance); summary and files changed; schema and contract changes; tests
added; exact commands with outcomes, including failed, skipped and interrupted checks; the acceptance checklist
with evidence; deviations (or none); blockers, attempted approaches and the attempt ledger
([budgets](budgets.md)); an outstanding-findings checklist; suggested follow-up, which authorizes nothing.

**PROGRESS:** the mutable index of active, completed, blocked and upcoming Goals with links and review outcomes.
**BACKLOG:** proposals, not authorization. **ROADMAP:** dependency order and any delivery barrier.

## Four distinct states

| State | Meaning | Who |
|---|---|---|
| Plan approval | The Plan may be implemented within its scope and budget. | Supervisor (ACCEPT on the Plan) |
| Readiness | The candidate passed its required local evidence and review; it may be integrated. | Supervisor pre-integration review |
| Conditional integration | Merged to the integration branch with required hosted evidence still pending. | Owner authorizes the merge |
| Final ACCEPT | The Goal is complete; dependents may proceed. | Supervisor, after the required integration disposition |

Only final ACCEPT completes a Goal. A merge, a passing pipeline or a delivered message is never acceptance.

## Lifecycle

1. The supervisor selects a dependency-ready Goal and writes the Goal and Spec. Major questions go to the owner.
2. The implementer inspects the repository and writes the Plan, unless the Goal explicitly authorizes the direct
   tier ([adoption](adoption.md#risk-tiers)). If the Goal exceeds reliable context, the Plan recommends a split.
3. The supervisor reviews and returns exactly one outcome: **ACCEPT**, **CORRECTION LOOP** or
   **ARCHITECTURE DECISION REQUIRED**. The accepted Plan bytes are imported into the integration branch.
4. The implementer implements, validates ([validation and integration](validation-integration.md)), self-reviews
   and records the Result. Escalation conditions override autonomy.
5. The supervisor reviews the actual diff and evidence. Passing tests alone are insufficient.
6. Corrections fix only the named findings and append to the Result. The same material issue surviving two
   correction cycles returns to Goal/Spec reassessment or escalation.
7. After the integration disposition, final ACCEPT; then closeout ([closeout and risks](closeout-risks.md)).

**Mandatory escalations:** architecture contradictions, scope expansion, security-model changes, destructive
migrations, public API or tool-contract changes, new major infrastructure or vendors, irreversible data-model
decisions. Plan approval never covers a change discovered afterward.

## Supervisor progress publication (option, enabled by default)

`SUPERVISOR_AUTO_PUBLISH` (default `true`) with an explicit `INTEGRATION_BRANCH`. When it is enabled, the
**supervisor**, **whenever it completes a PROGRESS update**, commits and pushes that update and its associated
management records (imported Results and status, reviews, decisions) to the integration branch from the main
integration checkout, without another owner confirmation.
- It verifies imported bytes, stages exact owned paths and excludes secrets and machine-local logs.
- It fetches and reconciles first and never force-pushes. A conflict, protected-branch rule or permission gate is
  reported, not bypassed.
- Publication is not review or ACCEPT. The implementer delivers Results and status and keeps its task branch and
  merge requests; this grants no direct implementer push.
- **Opt-out:** the owner may set it to `false` for the repository, or disable it for an explicit task or session;
  the override is recorded.
- It is an agent workflow, not a watcher, commit hook or scheduler. The supervisor assesses whether the update
  touches active task bindings and notifies the coordinator at a safe point.

## Supervisor checkout, delegated review and automatic relay

- The supervisor normally works in the **main integration checkout**. Specifications and read-only reviews need
  no separate worktree. A supervisor worker that genuinely needs isolation follows the worker-root rules in
  [coordination](coordination.md#naming-dispatch-and-relocation-gate).
- Prefer **bounded subagents** for Spec drafting/research and formal Plan/Result reviews. Reviewers are
  read-only by default; one writer per artifact. The supervisor integrates findings, owns the disposition and
  records it. A child reviewer cannot approve anything.
- **Review-ready submissions.** When an existing handoff or status check shows a review-ready Plan or Result, the
  supervisor starts a delegated review **without waiting for another owner prompt**:
  1. Verify the exact artifact (path and SHA-256) and its phase. Unfinished work is not reviewed as final.
  2. If the same bytes already received a completed review, record "duplicate unchanged review skipped" and
     point at the existing record.
  3. If delegation is unavailable, record that limitation and review directly rather than leaving authorized work
     idle.
  4. Record the disposition in a review file (template `results/REVIEW.md.tmpl`).
- **Automatic relay.** After recording, the supervisor relays the decision, reviewed inputs, permitted next
  action and remaining gates to the verified coordinator, through the companion messaging skill
  ([claude-session-handoff](../../claude-session-handoff/SKILL.md)). Receipt and acknowledgment are verified and
  recorded; pending or unavailable delivery is reported, never auto-resent, and never answered by creating a
  session.
- The owner may interrupt or redirect at any time. Mandatory escalations and owner merge authority remain. This
  adds no background watcher, no transport and no implementation authority before Plan approval.

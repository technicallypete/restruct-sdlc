---
name: sdlc-management
description: Establish or adapt a repository's agent-driven software delivery management structure (owner, supervisor, coordinator and worker roles; Goal, Spec, Plan and Result artifacts; budgets; validation, integration and closeout policy) from parameterized templates. Use when adopting this workflow in a repository, instantiating management files, or applying its lifecycle rules; not for session messaging (use claude-session-handoff) or resuming supervision (use repository-supervisor).
license: MIT
metadata:
  version: "0.1.0"
---

# SDLC management

This skill packages a management workflow for repositories where a human owner directs, a supervisor agent owns
Goals, Specs, reviews and progress, and an implementer agent owns Plans, code, validation and Results. It provides
policy references, parameterized templates and a stdlib checker. It contains no transport code, assigns no role and
grants no authority by being loaded.

## Boundaries

| Skill | Responsibility |
|---|---|
| `sdlc-management` (this) | Management structure, policy templates and lifecycle rules. |
| [repository-supervisor](../repository-supervisor/SKILL.md) | Resuming supervision from records; reviews, dependencies and progress. |
| [claude-session-handoff](../claude-session-handoff/SKILL.md) | Verified session discovery and routing, receipts, coordinator pin and closeout archiving. |

Load this skill alone for adoption or lifecycle questions. Load a companion only when its job is needed (messaging or
supervision); routine status checks never require reloading all three.

## When to use

- Adopting the workflow in a new or existing repository.
- Instantiating a Goal, Spec, Plan, Result, review or progress archive from the templates.
- Applying budget, validation, integration, coordination or closeout rules during a Goal.

Not for: product or architecture decisions, permission or provider changes, creating sessions, or CI redesign.

## Inputs

A parameter file copied from [parameters.example.json](templates/parameters.example.json): project name, release,
actor names, canonical sources, service roots, branches, CI provider and commands, validation options, budget and
effort defaults, and an optional delivery barrier. Every value is explicit; there are no hidden project defaults.

## Authority precedence

Harness and platform instructions, then explicit owner direction, then the adopting repository's canonical
governance and decisions, then this skill and its templates. A policy change records its true scope and authority.

## Adoption procedure (summary)

1. Read existing governance; record parameters and adoption authority in a Plan.
2. Install the three skills flat into `.agents/skills/` **without overwriting**: absent skills are copied,
   identical ones left alone, differing ones kept for a recorded owner decision, symlinked destinations refused.
3. Render each template to its destination; **create only missing files**. An existing file gets
   `<path>.sdlc-proposed` and a recorded owner merge decision.
4. Append the ignore lines; create the release directories.
5. Run the checker in adoption mode and fix every finding.

Full procedure, destination rule, risk tiers, installation limits and foundation-skill composition:
[adoption](references/adoption.md).

## Lifecycle summary

Goal and Spec (supervisor) → Plan (implementer; omitted only when the Goal explicitly authorizes the direct
tier) → Plan review (ACCEPT, CORRECTION LOOP or ARCHITECTURE DECISION
REQUIRED) → implementation and validation → Result → pre-integration review → conditional integration (owner
merge) → final ACCEPT → closeout. Only final ACCEPT completes a Goal. Review-ready submissions trigger delegated
review and automatic decision relay without another owner prompt; the supervisor keeps the review turn open with the
harness's asynchronous wait/notification interface and relays before its final reply (no repeated polling; an ended
turn may not wake automatically). An interruption alone is not stop-all: inspect child status and preserve completed
or authorized running work unless an explicit stop-all or conflicting direction applies. Owner interruption and
mandatory gates remain.
By default (`SUPERVISOR_AUTO_PUBLISH=true`, owner may disable) the supervisor pushes each completed PROGRESS update and
its management records to the explicit integration branch; the implementer keeps its task branch and merge requests.
Relayed owner authorizations are attributed truthfully and never override native permission gates.
By default (`OBSERVER_AUTO_ACTIVATE=true`, separate option) the companion milestone observer starts only after the
coordinator and supervisor bindings are explicitly verified; otherwise it stays inactive and reported. Fresh
`start` begins at the current transcript tail; deliberate catch-up after stopping uses `start --resume`. Notices
include failures and explicit decision/approval requests, with no approval authority. Follow the companion's
[observer procedure](../claude-session-handoff/SKILL.md#coordinator-milestone-observer-opt-in-here-an-adopting-repository-may-default-enable-it-after-verified-bindings)
for detection limits, preserved deduplication and fail-closed recovery. Effort by role: coordinator high (xhigh when planning), planning workers xhigh, implementation workers high.
Details: [roles and lifecycle](references/roles-lifecycle.md).
After verified terminal closeout, retain compact attributable evidence and purge redundant task-owned local
validation output by default; protect active inputs and session archives. See [evidence cleanup](references/closeout-risks.md#local-validation-evidence-retain-a-compact-record-purge-bulk-output).
Record resource ownership at creation and use [bounded routine cleanup](references/closeout-risks.md#bounded-routine-cleanup):
one scoped pass, a compact receipt, and individual holds instead of another verification campaign.

Validation follows [Git-first provenance and proportionate coverage](references/validation-integration.md):
assess target deltas before batches, reconcile relevant/unknown changes and always reconcile before final/MR.
Select expensive CI meta-tests by their actual dependencies; retain required application/security evidence.
Existing approved bindings remain in force until explicitly amended.

## References

| Reference | Covers |
|---|---|
| [roles-lifecycle.md](references/roles-lifecycle.md) | Ownership matrix, eleven Goal fields, Spec/Plan/Result contents, IDs and history, four states, precedence, delegated review and relay. |
| [budgets.md](references/budgets.md) | B3/B5/B7/B15, checkpoints, Goal-level attempts, shared allowance, extensions, ledger, effort. |
| [adoption.md](references/adoption.md) | Parameters, risk tiers, procedure, installation and helper path limits, composition with foundation skills. |
| [coordination.md](references/coordination.md) | One coordinator, one owner per task, recovery, receipts versus acknowledgment, the naming, dispatch and relocation gate. |
| [validation-integration.md](references/validation-integration.md) | Pre-batch reconciliation, finish-fix-rerun-advance, manual feedback order, merge requests, options, GitLab/glab adapter. |
| [closeout-risks.md](references/closeout-risks.md) | Verified cleanup, archive-before-prune, PROGRESS compaction, risk and performance reporting. |

## Templates

| Template | Destination |
|---|---|
| [root/AGENTS.md.tmpl](templates/root/AGENTS.md.tmpl) | `AGENTS.md` |
| [root/CLAUDE.md.tmpl](templates/root/CLAUDE.md.tmpl) | `CLAUDE.md` |
| [root/gitignore.lines](templates/root/gitignore.lines) | appended to `.gitignore` |
| [management/BUDGET_POLICY.md.tmpl](templates/management/BUDGET_POLICY.md.tmpl) | `management/BUDGET_POLICY.md` |
| [management/SUPERVISOR-HANDOFF.md.tmpl](templates/management/SUPERVISOR-HANDOFF.md.tmpl) | `management/SUPERVISOR-HANDOFF.md` |
| [release/ROADMAP.md.tmpl](templates/management/release/ROADMAP.md.tmpl) | `management/<release>/ROADMAP.md` |
| [release/PROGRESS.md.tmpl](templates/management/release/PROGRESS.md.tmpl) | `management/<release>/PROGRESS.md` |
| [release/BACKLOG.md.tmpl](templates/management/release/BACKLOG.md.tmpl) | `management/<release>/BACKLOG.md` |
| [goals/GOAL.md.tmpl](templates/management/release/goals/GOAL.md.tmpl) | `goals/<ID>-<stem>.md` |
| [specs/SPEC.md.tmpl](templates/management/release/specs/SPEC.md.tmpl) | `specs/<ID>-<stem>-spec.md` |
| [plans/PLAN.md.tmpl](templates/management/release/plans/PLAN.md.tmpl) | `plans/<ID>-<stem>-plan.md` |
| [results/RESULT.md.tmpl](templates/management/release/results/RESULT.md.tmpl) | `results/<ID>-<stem>-result.md` |
| [results/REVIEW.md.tmpl](templates/management/release/results/REVIEW.md.tmpl) | `results/<ID>-implementation-codex-review.md` and other reviews |
| [archive/PROGRESS-ARCHIVE.md.tmpl](templates/management/release/archive/PROGRESS-ARCHIVE.md.tmpl) | `archive/PROGRESS-YYYY-MM-DD.md` |
| [docs/RISKS.md.tmpl](templates/docs/RISKS.md.tmpl) | `docs/RISKS.md` |
| [docs/agents/BRANCH-WORKFLOW.md.tmpl](templates/docs/agents/BRANCH-WORKFLOW.md.tmpl) | `docs/agents/BRANCH-WORKFLOW.md` |
| [docs/agents/CLAUDE-SESSION-HANDOFF.md.tmpl](templates/docs/agents/CLAUDE-SESSION-HANDOFF.md.tmpl) | `docs/agents/CLAUDE-SESSION-HANDOFF.md` |

Templates use the `.tmpl` suffix so agents never read them as directory-scoped instructions in skill storage.

## Supported limits

Tested on Linux/WSL with Python 3 (standard library) and Git. Messaging and closeout depend on the companion
helper's verified Claude Code versions and its committed path under `.agents/skills/`. Not supported: other install
paths, native `.claude/skills/` discovery, discovery after `cd`, personal installation, macOS or native Windows,
and unverified CLI versions. See [adoption](references/adoption.md#installation-storage-versus-discovery).

## Package verification

[scripts/check_sdlc.py](scripts/check_sdlc.py) prints a JSON summary; exit 0 passes, 1 reports findings, 2 is a
usage error. Run it with `python3 -B` so no bytecode lands in the skill directory.

```sh
python3 -B scripts/check_sdlc.py package PATH [--skills-root DIR] [--literals FILE]
python3 -B scripts/check_sdlc.py adoption REPO --release NAME [--literals FILE]
python3 -B -m unittest discover -s scripts -p 'test_check_sdlc.py'
```

For a Git-backed bundle, verify a copy without its VCS metadata rather than weakening the check, for example
`rsync -a --exclude=/.git BUNDLE/ /tmp/bundle-check/ && python3 -B scripts/check_sdlc.py package /tmp/bundle-check`.
`package` checks a skill directory or a bundle root: frontmatter, the 200-line limit, intra-package and sibling-skill
links, template placeholders and adoption links, reachability, file types, forbidden content and the bundle
manifest. `adoption` checks an instantiated repository: required paths, rendered links, leftover placeholders, Goal
fields, ignore lines and forbidden content. Tests: [scripts/test_check_sdlc.py](scripts/test_check_sdlc.py).

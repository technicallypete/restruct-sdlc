# Budgets and proportional process

Budgets detect thrashing, scope growth and failing strategies. They are maxima, never productivity targets, and
never a reason to weaken validation, security or acceptance criteria. The adopted policy file is instantiated from
`templates/management/BUDGET_POLICY.md.tmpl`; the default class is the `DEFAULT_BUDGET` parameter.

## The unit: a Goal-level execution attempt

- One attempt is one Goal-level try at the outcome. **Commands, test batches, inner implement/test/fix loops,
  rebases, handoffs, checkpoints, context compaction and session restarts do not consume attempts.**
- The initial authorized implementation is attempt 1. An attempt ends when a review-ready Result is submitted,
  when the attempt is reported unable to satisfy the Goal, or when its material strategy is abandoned.
- A new attempt is consumed by a retry after an unsuccessful attempt or by a supervisor-authorized correction
  round. Calling an abandoned strategy "the same attempt" is not allowed.
- **Workers share the allowance.** Subagents and parallel workers contribute to the parent attempt; nobody gets
  an independent counter, and their loops are not summed into the total.
- Planning consumes no implementation attempt; neither do Plan corrections.

## Classes and checkpoints

| Class | Maximum attempts | Checkpoint | Typical use | Typical delegation |
|---|---|---|---|---|
| B3 | 3 | after attempt 2 | narrow configuration, small bug fixes, isolated presentation work, tooling | 0–1 |
| B5 | 5 | after attempt 3 | ordinary features, bounded infrastructure, integrations | 0–2 |
| B7 | 7 | after attempt 4 | authorization, isolation-sensitive work, migrations, cross-service work | 1–3 |
| B15 (optional, exceptional) | 15 | after attempts 8 and 12 | intentionally coupled foundation work | 2–4 |

The supervisor assigns the class in the Goal; the implementer may recommend a change during planning but never
changes an approved budget. A checkpoint is a reassessment, not an automatic stop: criteria done and remaining,
failures and repeated patterns, uncertainty, convergence and whether the Goal is still well bounded.

## Exhaustion and extensions

On exhaustion before all criteria pass: stop, preserve the working state, keep every failing criterion, update the
Result (attempts used, contributions per attempt, criteria satisfied and remaining, blockers, attempted approaches,
recommended next action) and return control to the supervisor.

An extension is explicit and exceptional. Its record states: previous budget, new budget, attempts already used
(historical counts preserved), reason, remaining work and the approving supervisor. **Counters are never reset**,
and an extension never authorizes scope, architecture or acceptance changes.

## Result ledger

Every Result carries an Execution Budget section (see `templates/management/release/results/RESULT.md.tmpl`):

```text
Budget class: B3   Maximum attempts: 3   Attempts used: 2 (second active)
Attempt log:
1. Initial implementation; batch B1 failed twice (fixture path, parser edge case), fixed and rerun;
   worker review contributed in this attempt; Result submitted; supervisor returned CORRECTION LOOP.
2. Authorized correction; rerun of affected batches; resubmitted.
Validation history (not counted): every failed, skipped and interrupted run with its evidence path.
```

## Effort

Effort is a **configurable recommendation** by role: `COORDINATOR_EFFORT` (default `high`) for orchestration,
status and handoffs; `PLANNING_EFFORT` (default `xhigh`) for planning workers, and for a coordinator that plans;
`IMPLEMENTATION_EFFORT` (default `high`) for implementation workers. Set worker effort explicitly through supported
controls where available instead of assuming inheritance. The owner may raise complex debugging or security work
to xhigh. Before a phase, state the intended effort and remind the operator; honor an already stated
choice. Verify actual runtime effort only where session metadata exposes it, and otherwise record "unknown". A
handoff's wording never sets or proves the runtime setting, and effort changes never reset budgets or completed
work.

## Workload-based model selection

Model choice is independent of effort and budget. With the owner's provider/model
selection, prefer a stronger reasoning model for complex architecture/security/data
planning, difficult test design and diagnosis, or repeated unresolved corrections.
Use the ordinary coding model for routine planning/implementation, precisely
specified fixes, test execution/reporting and coordination. For Claude, the
owner-approved examples are Fable 5.1 for the former and Opus 5.5 for the latter;
verify current availability before adopting these examples in another project.

Apply the configured role effort separately. State model/effort before a new phase,
honor owner choices and verify actual configuration where supported, otherwise
record unknown. Never assume an instruction changed a worker's runtime. Do not
interrupt an active batch, redo completed work, reset budgets or weaken gates
solely to change models. A stronger model does not accelerate the underlying
Docker/build/test process. These recommendations add no provider dependency or
automatic configuration change.

## Proportional process

An owner range/epic mandate never combines, resets or extends individual Goal
budgets. Assign each newly specified Goal its normal class; exhaustion and
owner work/phase/endpoint stops still hold while a broader mandate is unfinished.

Scale Plan and evidence detail to scope and risk ([risk tiers](adoption.md#risk-tiers)). Reference unchanged
accepted controls by path and version instead of rebuilding them. After the initial reading, re-read only changed
sections and unresolved findings. A new execution framework or orchestration library is separate scope, not an
incidental prerequisite.

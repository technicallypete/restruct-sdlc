# Validation and integration

Generic policy first, then the configurable options, then a concrete GitLab/glab adapter. Other providers are
adaptation points: replace the adapter commands with the provider's equivalents; nothing else here is claimed for
them. The instantiated runbook is `templates/docs/agents/BRANCH-WORKFLOW.md.tmpl`.

## Owner mandate and stop bounds

Check [recorded mandates/stops](roles-lifecycle.md#bounded-specification-authority-and-owner-stop-boundaries)
before every continuation. A ready Spec/accepted Plan or green pipeline does not
override an owner stop. Do not start successor lookahead while finishing the
endpoint task's CI/closeout. Auto-specification needs explicit bounded owner
authority; an epic mandate neither expands membership nor resets Goal budgets.

## Planning overlap

At the first predecessor implementation MR (drafts included), apply
[automatic planning](roles-lifecycle.md#automatic-planning-after-integration)
for the next eligible existing Goal/Spec; integration is fallback discovery only. Provisional planning may overlap CI,
acceptance and cleanup. Implementation may overlap predecessor staging CI after
reviewed source integration and supervisor release under the policy below. Do not reserve the shared test
stack or repeat predecessor validation merely to write the next Plan.

## Reassessment and execution release

After reviewed predecessor source integration, automatically reassess the
provisional Plan; permit isolated implementation during predecessor staging CI using [the release policy](roles-lifecycle.md#automatic-reassessment-and-execution-release).
Material Plan changes require bounded implementer updates and review; unchanged
design requires reconciliation only. Verify every execution gate and record/
relay the supervisor release before work, without another routine owner prompt.
Predecessor final ACCEPT still gates successor integration/final acceptance. A failed
predecessor gate pauses affected work only. The predecessor implementation owner
keeps its staging repairs and attempt ledger, working in parallel with the successor;
do not shift repair responsibility to successor workers. Preserve separate resources. Use existing binding and focused validation; no unchanged full rerun for a SHA.

## Git-first provenance

For new work, Git is the source of truth for committed code and management
artifacts. Bind reviewed inputs by repository, commit and path; record the tested
candidate and fetched target commit in the Result. A commit identifies bytes, not
approval or passing tests. Check for relevant tracked/untracked changes before
claiming a run tested that commit; commit scoped implementation checkpoints before
final qualification rather than building another source-tracking framework.

Record actual commands, outcomes (including failures/interruptions), relevant tool
versions, image IDs/digests and non-secret runtime configuration references in a
compact Result. Link required CI jobs and selected proof artifacts. Git does not
capture external runtime inputs or establish what executed.

Snapshot/hash only relevant inputs not identified by Git: reviewed uncommitted
changes, external configuration/fixtures or mutable artifacts. Preserve necessary
bytes when verification or a dependent task needs them; a hash alone is not
recoverability. Use existing secret-safe private handling for credentials; never
commit secrets. Do not inventory/hash every committed file again, archive whole
checkout copies or create a parallel evidence registry by default.

Retain compact attributable outcomes and necessary proof, then use the existing
closeout policy to purge disposable local bulk output. Do not erase failed-run
history or treat a changed commit SHA alone as reason to repeat unchanged tests.

This default applies to new Goals/Plans. Existing approved snapshots, wrappers,
retention rules and exact input bindings remain required unless explicitly amended
and reviewed; active work is not silently rebound or replanned. Security/authority,
acceptance, rebase, CI and resource-safety gates are unchanged.

## Before every batch

A batch is a named group of local checks (focused tests, builds, lint, controls, full runs). Before launching each
batch on a temporary Goal branch:

1. Fetch the remote target (`origin/<INTEGRATION_BRANCH>`).
2. Assess the exact fetched target delta against tested behavior, check dependencies,
   fixtures/contracts, build/runtime configuration, external inputs and required evidence,
   plus the task's authority, dependencies, approved bindings and governance. If all are
   demonstrably unaffected, record target range/candidate/reason in the existing Result
   and defer rebase/input reconstruction. Otherwise rebase/reconcile before testing.
   Unknown impact follows reconciliation. Preserve dirty work and immutable bindings;
   never rewrite a protected branch or change a running test's checkout.
3. Run `PRE_BATCH_ENV_CHECK` when configured; if it fails, do not launch.
4. Record target and candidate SHAs and the binding provenance with the batch evidence.

Read-only Git, input-integrity and resource-safety inspections may precede the rebase. No redundant rebase when the
target has not moved. Always reconcile before final qualification and again before
MR opening, rerunning affected checks only. No directory-wide management/skills exemption.
Existing approved active contracts retain their required sequence until explicitly amended.

## Reuse existing coverage during planning

### Early risk review and short correction loops

Use the existing Plan and review, rather than another checklist artifact:

- Review changed trust boundaries first: what can a malicious tenant, domain/DNS
  owner or credential holder now control, capture or replay? Check global identity
  separately from credential authority. Include affected migration/legacy-row,
  revocation and downgrade behavior when durable security state changes.
- Order approved implementation to prove the riskiest end-to-end path and its
  principal denial early, before surrounding features. Use existing fixtures and
  a thin functional slice; no planning-time build/probe or extra test campaign.
- Inventory affected callers, schema/version/count pins and actual executable
  selectors during planning using bounded searches. Include necessary paths in
  the approved touch-list; discovered design/scope gaps still stop affected work
  for review, rather than granting unrestricted file access.
- Keep a worker on a bounded coherent phase, with the existing context checkpoint
  and compact handoff at safe boundaries. Do not rotate useful workers merely
  per phase, forward entire transcripts or restart attributable tests/budgets.
- Diagnose and rerun the failed selector first. Reuse unchanged passing evidence;
  broaden only for a concrete changed dependency/guarantee under the existing
  supervisor exception rule. No broad run just for a fresh wrapper PASS.
- Batch related findings from the current bounded review into one actionable
  correction handoff with the guarantee, relevant files and minimum evidence.
  Consolidate available independent findings; do not serialize avoidable nudges
  or delay an urgent security hold waiting for unrelated review completion.

Apply these as improvements to existing execution, not a new approval stage,
mandatory phase-agent scheme, monitoring system, metric/reporting requirement or
framework. For active work, assess only the remaining delta at a safe boundary;
do not restart completed planning or running validation to satisfy this guidance.

Before proposing tests, inspect the relevant existing suites and fixtures. In the
Plan's existing validation/AC mapping, cite test paths or check IDs and distinguish
**reuse**, **extend**, and **new** coverage. State the actual uncovered behavior or
regression that each new case proves; prefer extending the existing fixture/test
at that boundary. One existing test may cover several acceptance criteria.

Do not clone a suite/fixture, rebuild an accepted invariant or add Goal-named
checks merely to give the new task its own evidence. Similar scenarios at distinct
boundaries (for example policy unit, runtime RLS and browser integration) may be
necessary: explain the distinct failure each catches. The supervisor requests a
bounded correction when proposed duplication has no such justification.

Record this in the normal Plan, not a new inventory/framework or planning-time
test campaign. Relevant regressions and required local/hosted/security coverage
remain mandatory; reuse of earlier passing results still requires reconciliation
of actual changed code, dependencies and runtime inputs. Test reuse is not a waiver
of current validation, manual feedback or evidence requirements.

## Proportionate coverage

Committed test/approval inputs use Git commit/path. Unconsumed status documents
need no duplicate test snapshot; approval/governance changes still require review.
Size local coverage to changed behavior, required security criteria and the actual
path/profile selection. Hosted staging is path-selected, docs-only pipelines may
be omitted, and cancellation is not passing-test evidence. Keep required local
coverage and honest failed/interrupted records; reuse unchanged attributable evidence.
The expensive CI meta-tests are distinct from application tests and may be selected
only for affected CI/harness/control dependencies; dependency and wrapper controls
remain separate obligations. Unknown dependencies select CI meta-tests. Existing
approved snapshots and Goal validation requirements are not silently waived.

## Finish, fix, rerun, advance

Within a batch, let ordinary failures finish collecting results. At the boundary, preserve every outcome and verify
owned cleanup. Gather all outstanding failures, fix them, rerun failed cases/controls and checks affected by the fixes,
then advance. Keep an outstanding-findings checklist in the Result. Unsafe or invalid work (resource or security
failures, corrupted evidence, fail-closed gates) stops immediately; dependent checks that cannot run are recorded as
blocked or skipped, never passing.

## Order of work

implementation → reconcile → focused checks → **required manual tests and operator feedback** → resolve findings
and repeat affected checks → reconcile again → required final local coverage → push and open the merge request.
Final qualification never starts while required feedback is pending. Evidence is reused only for unchanged
relevant content and inputs, with recorded provenance; a changed commit SHA alone does not demand an unchanged full
rerun.

## Integration

- **Safekeeping pushes.** After each implementation or correction round, commit scoped work and push a checkpoint
  to the temporary branch. A checkpoint opens no merge request and authorizes nothing.
- **Reviewed integration.** After the supervisor's pre-integration review, check the target again; if it advanced,
  rebase and rerun only affected checks. Push and open the merge request to `INTEGRATION_BRANCH` with source-branch
  deletion enabled. Before merging, inspect outstanding automated review findings and unresolved threads; passing
  CI does not dispose of them. Merge only with owner authorization.
- **Promotion** from `INTEGRATION_BRANCH` to `RELEASE_BRANCH` uses a separate merge request that **retains** the
  source branch. Long-lived branches (`PROTECTED_BRANCHES`) are never deleted or rewritten.
- **Cleanup.** Delete only verified merged temporary branches, after checking the exact remote tip.
- **Target advances.** When the integration branch advances, the supervisor assesses the delta against every active
  task: unaffected work continues; relevant changes reconcile at a safe boundary; conflicts pause immediately.
  Interrupted tests stop, reap owned children, preserve evidence and release locks before any rebase.

## Options

| Option | Values | Meaning |
|---|---|---|
| `FINAL_VALIDATION_PLACEMENT` | `mr-hosted` (default) | Required full coverage runs in the hosted merge-request pipeline before merge. |
| | `local-before-mr` | A solo-operator placement: required affected/full coverage runs locally before the merge request; the merge-request fast job runs automatically; the integration branch's post-merge pipeline supplies hosted evidence after a conditional integration. |
| `CANCELED_PIPELINE_SATISFIES` | `false` (default) | Final validation needs `success`. |
| | `true` | An owner-canceled post-merge pipeline also satisfies the gate. It is recorded as canceled, never as passing, and any failed job or known failing check still fails. Pending or running never qualifies. |

## GitLab/glab adapter (`CI_PROVIDER=gitlab`, `MR_TOOL=glab`)

```sh
git fetch origin || exit 1                                       # stop: never rebase against stale refs
git merge-base --is-ancestor origin/INTEGRATION_BRANCH HEAD || git rebase origin/INTEGRATION_BRANCH
git push origin HEAD:refs/heads/TEMP_BRANCH                      # safekeeping checkpoint
glab mr list --source-branch TEMP_BRANCH --target-branch INTEGRATION_BRANCH   # avoid a duplicate MR
glab mr create --source-branch TEMP_BRANCH --target-branch INTEGRATION_BRANCH \
  --title "TITLE" --description "Evidence: see the Goal Result." --remove-source-branch --yes
glab mr view MR_IID --comments                                    # automated review findings before merge
glab mr merge MR_IID                                              # only with owner authorization
glab ci status --branch INTEGRATION_BRANCH                        # post-merge disposition
glab mr create --source-branch INTEGRATION_BRANCH --target-branch RELEASE_BRANCH --title "Promote"
```

For the promotion request, confirm that source-branch deletion is **off**; a project-wide deletion default also
applies to that target, so check the setting rather than assuming the target changes it.

A published, owned temporary branch that must be rebased is pushed with an exact expected-tip
`--force-with-lease=TEMP_BRANCH:<old-sha>`, never an unconditional force. Hosted quota exhaustion is a resource
stop, reported as such.


## Validation economy and recurring failures

Before a batch, choose the smallest checks covering the actual change and required
security/shared boundaries. During diagnosis run the failed scenario and adjacent
cases first; expand only for affected dependencies, unresolved failures or required
final coverage. Reuse valid unchanged evidence with source/input provenance. Do
not create another benchmark, harness proof campaign or duplicate full run merely
for a new SHA or policy edit. Existing path selection and Goal requirements govern.

A passing retry does not establish a root cause or prove a flake fixed. Inspect
failure output first. Under standing integration authority, the supervisor may
approve one retry of the failed job for an evidenced transient/unrelated failure,
within the existing Goal budget; retain both outcomes and record the hypothesis.
No blind repeated retries, whole-pipeline rerun when one job suffices, or treating
an unknown failure as unrelated. A recurrence requires focused diagnosis and a
bounded repair/disposition before another retry. Scope/security/budget and native
permission stops still apply; repeated-issue escalation remains in force.

On GitLab, for non-executable workflow-prose publication only, the supervisor may
use `git push -o ci.skip` after reviewing the entire staged delta and verifying no
application, tests/fixtures, executable scripts/templates, CI selectors, dependency
or runtime inputs changed. Markdown filename or management/skills location alone
is insufficient. Record the exact skipped publication and reason; skipped is not
passing and cannot satisfy or erase a required application staging gate. Unknown
impact follows normal CI. This exception does not change the path selector.

Cancel a superseded duplicate hosted run only after verifying the newer run covers
its exact changes and required suites, the older run has no failed required check,
and no independent qualification depends on it. Record both pipeline IDs and the
cancellation; preserve failed-run evidence and the still-required qualification.

## Focused selection before the first run

Focused checks are the default for **every local run**, including initial
implementation, corrections and final local qualification. Start with changed
behavior and required technical guarantees, then choose the smallest existing
package/test filters, service checks, browser projects and integration entrypoints
that cover them. Inspect what the command actually runs; a narrow task name or
"focused batch" label does not make an umbrella command narrow.

Before Plan approval and before launching a batch, the supervisor/coordinator
checks the proposed executable selectors against that scope. Reject unexplained
`all`, generic unit/migration/ops suites or full control suites when they include
unaffected work. Prefer supported filtered/direct existing test commands; record
coverage and required setup in the normal Plan/Result, without a new checklist,
manifest, test wrapper or reporting stage. Reuse valid attributable prior passes.

A broad local run is an exception requiring a concrete technical reason and
supervisor disposition **before launch**: for example a changed shared boundary,
a specified indivisible guarantee, or an identified unresolved dependency impact.
State what wider coverage is needed and why the narrower checks cannot establish
it. Existing reviewed Plan justification can supply that disposition; do not ask
again for an unchanged approved exception. Tool convenience, "to be safe", a fresh
wrapper PASS, or an unavailable narrow harness selector alone is not justification.
If selection is unavailable, report the exact limitation once and propose the
smallest safe existing command for supervisor disposition; do not automatically
fall back to the broad suite or modify the harness to add another framework.

If an overbroad run is already active, retain completed evidence and narrow its
remaining work at a supported safe boundary with owned cleanup. Required schema
setup, real affected regressions and atomic/global guarantees remain; never mark
unexecuted checks passed. Mandatory hosted MR/integration jobs retain their actual
configured scope. This is local selection policy, not permission to skip required
CI, weaken security evidence or change budgets. Apply to active tasks at the next
safe boundary; reassess inherited umbrella selections without a full replan.

## Targeted reruns and attributable coverage default

After failures, rerun the smallest failed case/control and checks affected by the
fix. Reuse unrelated passing results with unchanged relevant code, schema,
fixtures, dependencies, configuration and runtime inputs. A suite, batch or job
name is not itself a reason to repeat every case. CI/harness self-tests follow
the same dependency rule; ordinary feature work does not automatically invalidate
the entire control suite. Unknown impact or a real shared dependency requires
broader relevant coverage, with the reason recorded.

Complete local coverage may combine earlier attributable passes and later focused
reruns. Record the original/rerun source and input provenance and outstanding IDs
in the existing Result/review, not a new registry or aggregation framework. Never
rewrite failed/canceled runs as successful, synthesize a full-pass report or use
an older pass to conceal a new substantive failure. Preserve known root-cause
uncertainty; a passing retry does not prove a flake fixed. Required atomic/global
checks still need their actual evidence, and required hosted jobs remain unchanged.

If a rerun is unnecessarily broad, preserve its completed outcomes and use
supported cancellation at a safe case/control boundary with owned cleanup; do not
interrupt unsafe-to-stop work or declare unexecuted cases passed. Required coverage
and unresolved failures remain gates. No full restart solely for a new SHA,
management edit, wrapper tally or clean summary when attributable coverage suffices.

When implementation is frozen, perform bounded read-only source review in
parallel with independent validation. Label preliminary source findings honestly;
final acceptance still waits for the Result, reconciled code/inputs, required
checks and automated-review findings. Review later changes as deltas rather than
repeating the unchanged source review. Preserve the current task, owner and budget.

Apply this default to active tasks at the next safe boundary and future tasks;
it supersedes generic wording to rerun an entire failed batch. If a specific Goal
needs one indivisible run for a technical guarantee, preserve that guarantee and
record the bounded exception. This policy adds no script, test stage or monitor.

# Validation and integration

Generic policy first, then the configurable options, then a concrete GitLab/glab adapter. Other providers are
adaptation points: replace the adapter commands with the provider's equivalents; nothing else here is claimed for
them. The instantiated runbook is `templates/docs/agents/BRANCH-WORKFLOW.md.tmpl`.

## Planning overlap

After verified integration, apply [automatic planning](roles-lifecycle.md#automatic-planning-after-integration)
for the next eligible existing Goal/Spec. Provisional planning may overlap CI,
acceptance and cleanup; implementation still waits for required final dependency
acceptance, Plan review and current input binding. Do not reserve the shared test
stack or repeat predecessor validation merely to write the next Plan.

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
owned cleanup. Gather all outstanding failures, fix them, rerun each failed batch and the checks the fixes affect,
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

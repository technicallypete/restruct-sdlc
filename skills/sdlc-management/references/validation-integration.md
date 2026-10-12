# Validation and integration

Generic policy first, then the configurable options, then a concrete GitLab/glab adapter. Other providers are
adaptation points: replace the adapter commands with the provider's equivalents; nothing else here is claimed for
them. The instantiated runbook is `templates/docs/agents/BRANCH-WORKFLOW.md.tmpl`.

## Before every batch

A batch is a named group of local checks (focused tests, builds, lint, controls, full runs). Before launching each
batch on a temporary Goal branch:

1. Fetch the remote target (`origin/<INTEGRATION_BRANCH>`).
2. `git merge-base --is-ancestor origin/<INTEGRATION_BRANCH> HEAD`; if it fails, rebase. Resolve conflicts while
   preserving both accepted changes, keep dirty work and immutable bindings, and reconcile changed approved inputs
   before testing. Never rebase a long-lived or protected branch.
3. Run `PRE_BATCH_ENV_CHECK` when configured; if it fails, do not launch.
4. Record target and candidate SHAs and the binding provenance with the batch evidence.

Read-only Git, input-integrity and resource-safety inspections may precede the rebase. No redundant rebase when the
target has not moved. Never edit or rebase a checkout underneath running tests.

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

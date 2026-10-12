# Restruct SDLC skills

Restruct SDLC is a bundle of three agent skills for repositories run by a human owner, a supervisor agent and an
implementer agent. Together they provide a management workflow (Goals, Specs, Plans, Results, budgets, validation,
integration and closeout), verified local session handoffs, and supervision recovery from repository records.

**Status: published.** Available on [GitHub](https://github.com/technicallypete/restruct-sdlc).

## Why Restruct?

Restruct™ is an operating methodology for AI-first software organizations that places architectural governance,
specification and human accountability ahead of implementation.

Restruct SDLC applies those principles to repository workflows. Goals and Specs define intent and boundaries;
Plans describe execution; Results and review records preserve evidence. A human owner retains architectural
authority, supported by a supervisor agent and an implementation coordinator. Budgets, verified handoffs and
cleanup keep execution bounded and context available across sessions.

This bundle implements the software-delivery workflow within Restruct's broader organizational methodology.
[Explore Restruct](https://vestive.com/restruct-methodology) or read the
[AI as Governed Execution chapter](https://vestive.com/restruct-methodology/ai-as-governed-execution).

## Skills

| Skill | Responsibility |
|---|---|
| [sdlc-management](skills/sdlc-management/SKILL.md) | Management structure, policy templates, lifecycle rules and the package/adoption checker. |
| [repository-supervisor](skills/repository-supervisor/SKILL.md) | Resume supervision from management records; review Plans and Results; track dependencies and acceptance. |
| [claude-session-handoff](skills/claude-session-handoff/SKILL.md) | Discover and check local Claude Code sessions, deliver authorized handoffs, verify receipts, pin a coordinator and archive delivery records. |

Each skill is independently useful. Loading a skill assigns no role and grants no authority.

## Requirements

- Linux or WSL2, Git, and Python 3 with the standard library.
- Claude Code 2.1.290, 2.1.291 or 2.1.296 for session messaging (the creation gate is verified on 2.1.296 only).
  Other versions fail closed in the handoff helper.

## Installation (flat, never overwriting)

Install each skill into the target repository's `.agents/skills/` and commit it. Run from this bundle's root:

```sh
TARGET=/path/to/target-repo
for s in sdlc-management claude-session-handoff repository-supervisor; do
  dest="$TARGET/.agents/skills/$s"
  if [ -L "$TARGET/.agents" ] || [ -L "$TARGET/.agents/skills" ] || [ -L "$dest" ]; then
    echo "STOP $s: symlinked destination; nothing copied"
  elif [ ! -e "$dest" ]; then
    mkdir -p "$TARGET/.agents/skills" && cp -R "skills/$s" "$dest" && echo "INSTALLED $s"
  elif [ -z "$(find "$dest" -type l)" ] && diff -r -q "skills/$s" "$dest" > /dev/null; then
    echo "IDENTICAL $s: left unchanged"
  else
    echo "COLLISION $s: existing content kept; record an owner merge or replacement decision"
  fi
done
```

Absent skills are copied and identical ones left unchanged. A differing existing skill (for example an edited helper) stays byte-identical: record the collision, its `diff -r` summary and the owner's merge or replacement decision before changing it. A symlinked `.agents`, `.agents/skills` or skill destination stops the install. Details: [installing the skills](skills/sdlc-management/references/adoption.md#installing-the-skills).

`.agents/skills/<skill>/` is the supported layout: Codex discovers repository skills there, and Claude sessions read
each `SKILL.md` explicitly as the adopted `AGENTS.md` instructs. This bundle's `skills/` directory is storage, not a
discovery location. The handoff helper's closeout command verifies the committed helper at
`.agents/skills/claude-session-handoff/scripts/handoff.py`, so other locations are refused.

## Verify

```sh
python3 -B skills/sdlc-management/scripts/check_sdlc.py package .
python3 -B -m unittest discover -s skills/sdlc-management/scripts -p 'test_check_sdlc.py'
python3 -B -m unittest discover -s skills/claude-session-handoff/scripts -p 'test_handoff.py'
```

`MANIFEST.tsv` lists every other file as `sha256<TAB>origin<TAB>path`, where origin is `new`, `verbatim` or
`adapted`. The package check verifies it.

## Adopt

Follow [the adoption reference](skills/sdlc-management/references/adoption.md): record parameters copied from
[parameters.example.json](skills/sdlc-management/templates/parameters.example.json), render the templates (creating
only missing files and proposing changes to existing ones as `<path>.sdlc-proposed`), then run
`check_sdlc.py adoption . --release <release>` in the target repository.

## Limits and unsupported cases

Not supported: install paths other than `.agents/skills/`, native `.claude/skills/` discovery, discovery after `cd`,
personal installation, macOS or native Windows, and unverified Claude Code versions. Helper conventions are fixed:
`G` plus three-digit task labels, documents under `management/`, review records named
`management/<release>/results/<ID>-implementation-codex-review*.md`, and Linux `/proc`. Coordinator relocation stays
deferred until a same-session restart from a moved path is verified locally. The GitLab/glab adapter is concrete;
other providers are adaptation points.

## License

MIT; see [LICENSE](LICENSE). Copyright (c) 2026 Vitruvian Technology, Corp.

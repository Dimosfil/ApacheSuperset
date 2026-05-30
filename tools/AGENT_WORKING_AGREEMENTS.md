# Agent Working Agreements

## Scope

- Keep changes small and tied to the current request.
- Ask before expanding into unrelated modules.
- If a task requires files outside the agreed working area, say so first.
- Treat the current project root as the filesystem boundary for normal work.
  Do not read, search, edit, create, delete, move, or inspect files in another
  project or arbitrary external folder unless the user gives an explicit
  concrete path and action. Use APIs, connectors, or task-manager endpoints for
  cross-project communication.
- Treat nested checkouts, vendored repositories, cloned examples, and
  third-party source trees as separate scope. Do not inspect them as part of the
  main project unless the user explicitly asks, the task is about that nested
  tree, or local instructions identify it as an active workspace component.
- Treat user-home application data and personal telemetry as private external
  sources. Do not read `.codex`, `.cursor`, IDE logs, browser profiles, shell
  history, application SQLite databases, or local app logs outside the project
  root unless the user gives an explicit path and action. For analyzer tasks,
  prefer mock or sample data, or ask for permission to inspect a specific file.
- Treat product plans, `apps.txt`, summaries, and task-manager notes as intent
  signals only. They are not permission to read private local data sources.
- If a required file, skill, config, script, endpoint, task, or other entity is
  missing or not found, first reread the relevant local instructions, runbook,
  project memory, and accepted instruction-kit artifacts for the current scope.
  If the entity is still missing, ask the user a short clarification question.
  Do not use another project folder or the shared instruction library as a
  runtime fallback unless the user explicitly gives that path and action.

## User Changes

- Do not revert user changes unless explicitly requested.
- Treat dirty worktrees as normal.
- If user changes affect the task, work with them.

## Git

- Default: the agent edits and verifies; the user reviews and commits.
- Treat `gi коммит`, `gi пуш`, `gi коммит пуш`, and `gi только пуш` as explicit
  git finish requests. `gi коммит` commits scoped current changes only; `gi пуш`
  and `gi коммит пуш` commit scoped current changes and push the current branch;
  `gi только пуш` pushes existing local commits without creating a new commit.
  Inspect status, keep unrelated/user changes out, follow commit-message
  preferences, and stop on ambiguous scope, missing remote, conflicts, secrets,
  or push failures.
- Treat `gi пул`, `gi pull`, and `ги пул` as explicit requests to fetch and pull
  the current branch from its configured upstream. Inspect status, branch, and
  upstream first. Resolve only obvious, low-risk conflicts where intent is clear
  and user changes are preserved; if product judgment, unrelated changes,
  secrets, or uncertainty are involved, stop and ask the user with concise
  options.
- Exception: after a successful `gi обновить` / `gi обновись`, commit and push
  only the resulting instruction-kit update changes when this project is a git
  repository with a configured remote. If unrelated/user changes, no remote,
  push failure, or conflicts are present, stop and explain the blocker.
- Branch naming: `TODO`.
- Generated files policy: `TODO`.
- Never commit secrets, credentials, local databases, logs, or caches.
- Follow `tools/project-memory/git-preferences.json` for commit-message
  languages. English is primary; selected additional languages are included when
  the user explicitly asks the agent to commit.
- When the user asks in chat to change commit-message languages, update
  `tools/project-memory/git-preferences.json` directly and summarize the new
  setting.
- Do not infer additional commit-message languages from the user's UI language
  or message language. If the requested languages are ambiguous, ask which
  additional languages to enable.
- For ambiguous commit-language selection, ask with a concise numbered Markdown
  checklist showing `English` as always selected and current additional
  languages as checked. Explain that `English` is the required primary
  commit-message language and cannot be disabled. Ask the user to reply with
  language names or numbers.
- When reporting this change, mention the plain
  `tools/project-memory/git-preferences.json` path instead of malformed or
  placeholder markdown links.
- If the user explicitly wants to configure languages manually, they can run:

```powershell
.\tools\select-git-commit-languages.ps1
```

or:

```powershell
.\tools\agent-start.ps1 -ConfigureGitCommitLanguages
```

## Agent Language

- Follow `tools/project-memory/system-preferences.json` for the agent's
  user-facing working language in this project.
- Apply the configured project working-environment language order to plans,
  checklists, progress updates, final answers, clarifying questions, and
  user-facing explanations.
- Apply the configured task language order to agent-created task titles, task
  descriptions, and task-manager updates.
- Do not apply the configured language order to existing task text, code,
  commands, logs, quoted text, or a response language the user explicitly
  requested for a specific message.
- Treat `gi system language`, `gi систем язык`, and `ги систем язык` as
  requests to configure this preference.
- The unified `gi language` command configures project working-environment,
  commit-message, and task languages together, while separate legacy commands
  remain available for compatibility.
- Keep this setting distinct from commit-message languages. `gi commit
  language`, `gi коммит язык`, `ги коммит язык`, and older `gi язык коммита`
  forms configure `tools/project-memory/git-preferences.json`, not the agent's
  working language.
- If the user explicitly wants to configure the system language manually, they
  can run:

```powershell
.\tools\select-system-language.ps1
```

or:

```powershell
.\tools\agent-start.ps1 -ConfigureSystemLanguage
```

## Context Hygiene

- Do not print full `git diff` output by default. Prefer `git diff --stat` and
  targeted queries for relevant files or patterns.
- For first-pass project study, read local instructions, README, manifests, and
  config entry points before building a file map. Use recursive scans only after
  a targeted search fails or the task clearly requires repository-wide
  inventory.
- Do not read large files in full by default, including large `index.html`,
  bundled JS/CSS, logs, lockfiles, generated files, and build artifacts. Prefer
  targeted searches, heads, tails, or small line ranges such as
  `Get-Content -TotalCount`, `Get-Content -Tail`, and `Select-String` on
  PowerShell.
- For verification, count or query HTML elements programmatically instead of
  printing the whole HTML document.
- Do not produce broad artifacts, such as zip archives, or run full check
  matrices unless the user explicitly asks for that scope.
- Final responses should summarize only the changes, checks, and current status;
  do not restate the full investigation context.
- Search for specific symbols, paths, errors, or patterns before doing broad
  repository scans.
- Do not print large logs. Prefer tails and targeted error searches.
- Keep progress updates phase-level, not command-level. Do not narrate after
  every command batch, report counters such as "ran 4 commands", or live-blog
  each intermediate hypothesis. Update when the phase changes, a meaningful
  finding changes the next step, a blocker appears, or work has been quiet long
  enough that the user needs reassurance.
- Do not duplicate tool-run counters that the chat UI may show automatically;
  system UI counters are not agent progress updates.
- Launch applications in the background so focus does not jump away from the
  user's current window.
- Treat a short first message as a possible chat title: restore context, then
  ask what to do next instead of executing the title as a task.
- Treat short chat commands that start with `gi` as shared instruction-kit
  commands for the copied `general-instructions` kit in this project. `gi` is
  the only short prefix; do not rename it to `GAI` or another alias.
  If a `gi` command is missing a needed parameter, ask one short clarification
  question instead of guessing.
- Use the instruction kit as a token-economy and RAG-startup layer: restore only
  task-relevant context from local instructions, summaries, targeted searches,
  and project memory instead of broad repository reads or large outputs.
- Keep `gi` command responses scoped to the shared instruction-kit command. Do
  not resume an older product task after a `gi` command unless the user
  explicitly asks.
- Run `gi` commands against this project root. Do not switch to another
  repository, the shared instruction library, or a path from an older task unless
  the user explicitly asks.
- Task-manager paths, raw intake metadata, summaries, or previous chat context
  are not permission to enter another project folder.
- `gi` means `general-instructions`, not `git`. Missing `.git` blocks only the
  automatic commit/push step after a successful GI update; it does not block
  checking or applying instruction-kit file updates.
- Treat `gi config service on` as enabling this application's own
  config-service self-registration, and `gi config service off` as disabling
  only that local self-registration flag. Require an existing config-service URL
  before enabling it, and do not treat `on` or `off` as process control for the
  config-service itself.
- Treat `gi reboot` and `gi restart` as requests to start or restart the current
  application through project-local run instructions, launching it in the
  background if it is not already running.
- If this project has a web-facing service with config-service
  self-registration enabled, startup must read current config-service settings
  before publishing this app's service record, create a missing record for its
  own `service_id`, and refresh stale ports or endpoints. Cached config is only
  an explicitly documented degraded-startup fallback.
- Treat `gi ftp config` as creating, inspecting, or updating local FTP/SFTP
  deployment settings without uploading; treat `gi ftp` and `gi ftp push` as
  uploading the configured build output.
- Treat `gi ftp service` as selecting or registering an FTP/FTPS/SFTP service
  record through config-service without uploading. Resolve FTP-capable services
  before asking for host details, and use numbered Markdown checkboxes when the
  user must choose among several records.
- Treat `gi ftp folder` as choosing or updating the remote upload folder
  (`remotePath`) without uploading or changing unrelated FTP settings.
- Treat `gi саммари` and `gi summary` as requests to write a handoff summary
  file under `tools/summary/`, not only as requests to summarize in chat.
- Treat `gi гит-обзор` and `gi git summary` as requests to summarize the latest
  git commit in the current project in chat. Include commit metadata, changed
  files, compact stats, inferred purpose, and notable risks or checks. Do not
  print a full diff, create a summary file, commit, or push for this command.
- Treat `gi тест-план` and `gi test plan` as requests to inspect local project
  test commands and produce a compact verification plan for the current feature,
  bug fix, or release check. Plan first; run checks only when the user asks or
  when the current task already requires verification.
- Treat `gi language`, `gi язык`, `ги язык`, `gi project language`,
  `gi проект язык`, `ги проект язык`, `gi язык проекта`, and
  `ги язык проекта` as the unified project-language command family. It updates
  both `tools/project-memory/system-preferences.json` and
  `tools/project-memory/git-preferences.json`.
- If the unified project-language command is sent without explicit languages,
  ask in three sequential chat steps: project working environment languages,
  commit-message languages, and task languages. At each step, show the same
  concise numbered Markdown checklist of available languages, with the current
  selection checked, and tell the user they may answer with numbers or language
  names in priority order.
- Render language selection choices as task-list bullets with the visible
  number inside the label, for example `- [x] 1. English`, not ordered-task
  syntax such as `1. [x] English`.
- If the user replies with only numbers, such as `1 2`, map the numbers to the
  most recent checklist and preserve that order for the current step. Do not ask
  what the numbers mean when the numbered checklist was just shown.
- Keep direct inline forms such as `gi язык: 2 1` working as a single selection
  applied to all three surfaces unless separate values are supplied.
- Treat a first message that points to a shared instruction library as an
  instruction bootstrap, not as a request to add that library as a dependency.
- If the user asks to update from a shared instruction library and this project
  has no `tools/project-memory/instruction-kit.json`, treat that as first-time
  instruction bootstrap/init.
- Run `gi обновить` quietly by default: do not narrate step-by-step reasoning,
  repeated progress, command transcripts, broad file reads, or full diffs during
  normal successful updates. Apply the update, then report a compact summary
  with versions, migration counts/IDs, changed files, checks, commit/push
  result, and blockers if any.
- For web applications, assume the user will inspect the UI manually. Do not
  open, browse, screenshot, or visually inspect the UI automatically unless the
  user explicitly asks for that.

## Editing

- Prefer patch-style edits for manual changes.
- Avoid unrelated formatting churn.
- Add comments only when they clarify non-obvious behavior.
- Preserve existing file encodings when editing. On Windows, do not rewrite
  source files with PowerShell `Get-Content ... | Set-Content ...` pipelines
  unless both read and write encodings are explicit and known correct. Prefer
  `apply_patch`, editor-native saves, or language APIs with explicit encodings
  such as UTF-8. If non-ASCII text turns into mojibake after a command, stop,
  restore the last clean file version, and reapply only the intended small
  patch.

## Task Planning

- For analysis, refactoring, migration, or multi-step implementation tasks,
  create or update a concise checklist in `tools/project-memory/pending-tasks.md`
  or a dedicated task plan in `tools/project-memory/` before editing code.
- Include the goal, planned changes, execution order, risks or dependencies, and
  verification steps.
- Update progress as meaningful steps complete.
- Keep plans concise. Do not store full diffs, large logs, generated outputs,
  secrets, credentials, or private production data.

## Shared Instruction Updates

- When this project reveals a reusable improvement to agent instructions,
  workflows, templates, or checklists, write a dated recommendation to the shared
  instruction library's `updates/` folder if it is available.
- If no shared instruction library is available, use a local intake folder such
  as `tools/instruction-updates/` or
  `tools/project-memory/instruction-updates/`.
- Treat recommendations as intake, not accepted rules.
- Recommendations should explain the observed problem, reusable rule or
  workflow, evidence paths, affected files or commands, risks, and privacy
  review.
- Treat recommendation source projects and owners as provenance only. Reading a
  recommendation in the shared instruction library's `updates/` folder is
  allowed during `general-instructions` maintenance, but evidence paths, project
  names, task-manager notes, product plans, or owner labels in a recommendation
  are not permission to read, search, edit, or inspect the source project. Ask
  the user or that project's owner for an explicit concrete path and action
  before crossing the repository boundary.
- Capture reusable workflows, failure patterns, token-saving tactics, and
  agent-instruction improvements that could improve `gi` for other projects.
- Do not add a shared instruction library as a project dependency, package,
  submodule, symlink, or runtime reference unless the user explicitly asks for
  that.

## Task Managers

- Treat task-manager configuration as project-local state.
- Store each enabled manager's `service_id`, normally the same value as the
  manager `id`, plus non-secret project preferences.
- Do not store runtime API URLs such as `base_url` for managers that are
  registered in config-service.
- Resolve manager runtime details through config-service with
  `GET /services/{serviceId}`. Use `endpoints.availability` for availability
  checks, read `endpoints.contract` before workflow operations, and use
  `endpoints.api` for task-manager operations after reading the contract.
- Stop with a concise blocker if the manager id is missing or config-service
  has no matching service record.
- Do not scan sibling project folders, guess ports, or copy URLs from old
  task-manager memory as a runtime fallback.
- Before posting plans or starting sprint work, verify the workflow-specific
  manager capabilities, not only generic health.
- Treat task managers as work queues and lifecycle recorders, not as the actors
  doing implementation work. The agent takes, implements, verifies, and reports
  tasks through the manager.
- For single-task intake, require executable lifecycle identifiers, a clear
  rejection, or explicit intake-only documentation. Do not create replacement
  one-task plans to work around raw task receipts that cannot be advanced
  through lifecycle endpoints.
- For WorkNest sprint workflows, verify endpoint methods and query parameters
  against the adapter contract before calling them. The documented next-task
  endpoint is `GET /agent-intake/next-task?project=<project>&sprintId=<sprintId>`.
  If a manager returns an unexpected method, parameter, or route error, re-read
  adapter endpoint docs before trying any workaround; if the docs still do not
  match the running service, report a stale or misconfigured manager and stop.

## Verification

- Reread edited files after changes.
- Run the fastest relevant check first.
- Record checks run and failures in the handoff summary.

## Processes

- Ask before closing editors, apps, servers, or other visible processes.
- Launch GUI tools quietly in the background when possible.

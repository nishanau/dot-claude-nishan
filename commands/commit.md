# /commit — Smart Commit

Pre-compute context first, then commit. Do not ask me questions — just do it.

## Steps

1. Run these in parallel to gather context:
   - `git status` (see what's changed)
   - `git diff --stat` (summary of changes)
   - `git diff` (actual changes for understanding)
   - `git log --oneline -5` (recent commit style)

2. Based on the diff, draft a commit message that:
   - Matches the existing commit message style in this repo
   - Summarizes the WHY, not just the WHAT
   - Is 1-2 lines max
   - Uses conventional format if the repo already does (fix:, feat:, docs:, etc.)

3. Stage only the relevant files (not `git add -A` — be selective, skip .env, credentials, large binaries).

4. Commit with the drafted message.

5. Report: what was committed, the message used, and current branch.

## Flags
- If I say `/commit --push`: also push to remote after committing.
- If I say `/commit --pr`: push and create a PR using `gh pr create`.
- If I say `/commit --amend`: amend the previous commit instead of creating a new one.

## Rules
- Never skip pre-commit hooks (no --no-verify).
- Never force push unless I explicitly say --force.
- If the hook fails, fix the issue and create a NEW commit (don't amend).

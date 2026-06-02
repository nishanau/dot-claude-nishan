# /review — Pre-PR Verification

Review the current branch against the plan/spec before creating a PR. This is the verification loop — confirm the work is actually complete.

## Steps

1. **Gather context** (run in parallel):
   - `git diff main...HEAD --stat` (all changes on this branch)
   - `git log main...HEAD --oneline` (all commits)
   - Find the plan file in `docs/plans/` if one exists for this work

2. **Check completeness against the plan**:
   - For each phase/task in the plan, verify:
     - Was it implemented?
     - Were the tests written?
     - Was the "done when" condition met?
   - Flag any plan items that are missing or incomplete.

3. **Run verification**:
   - Run the full test suite. Report results.
   - Run type checks (tsc --noEmit for TS projects, ruff for Python).
   - Check for console.log / debug print statements left in code.
   - Check for TODO/FIXME comments that should have been resolved.

4. **Check for common issues**:
   - DB migrations included if schema changed?
   - .env changes documented?
   - No secrets committed?
   - No large files or binaries staged?

5. **Report**:
   ```
   ## Review Summary
   
   **Branch**: feature/xyz (5 commits ahead of main)
   **Plan**: docs/plans/2026-05-22-feature-xyz.md
   
   ### Completeness
   - [x] Phase 1: User model changes — done, 3 tests passing
   - [x] Phase 2: API endpoints — done, 5 tests passing
   - [ ] Phase 3: Frontend integration — 2 of 4 components done
   
   ### Verification
   - [x] Tests: 42 passing, 0 failing
   - [x] Type check: clean
   - [ ] ISSUE: console.log on line 45 of api/views.py
   
   ### Verdict: NOT READY — Phase 3 incomplete, debug statement found
   ```

6. If everything passes: suggest creating the PR with a draft title and body.

# Global Instructions

## About Me
- ICT Infrastructure Engineer who dabbles who also builds apps for internal use at work or personal projects, on Windows 11 (bash shell via Git Bash)
- Projects: Django monorepo (Shiploads), Shiploads website, Shiploads mobile app (Expo/React Native), MCP server (Python), Football webapp, SuppliesFixturesFirstAid fullstack
- Primary languages: TypeScript, Python, HTML/Django templates
- Tools: uv (Python), npm/pnpm (JS/TS), git, make, pytest

## Execution Style
- Execute inline and directly. Do NOT spawn subagents, nested skills, or brainstorming phases unless I explicitly ask.
- Show progress as you go. No invisible state-checking or skill-loading.
- If I give you a plan or spec file, follow it phase by phase. Don't re-plan or re-scope it.
- When I ask for implementation, implement. Don't ask if I want a plan first.

## System Design First Principles
- When planning and implementing coding tasks, plans and specs, always use system design first principles. These principles are the bedrock of how you build and maintain anything.

## Planning First
- For any multi-step task, enter plan mode first. Present the plan, wait for my approval, then execute.
- Architectural understanding before implementation — always.
- Break plans into independent phases with commit points between them.
- Each phase should be self-contained so context can be cleared between phases without losing progress.
- Write plans to a file (docs/plans/) so they persist across sessions and context clears.

## Scope Discipline
- Before big tasks, confirm scope: which files/apps/directories are in play.
- Don't expand beyond what's asked. Don't refactor surrounding code. Don't add unrequested features.
- Analysis-only when asked for analysis. Changes-only when asked for changes.

## Debugging Protocol
- NEVER apply a fix without first confirming root cause.
- Step 1: Reproduce — identify exact steps/input that trigger the bug.
- Step 2: Trace — add logging/console output at key points to narrow the cause.
- Step 3: Diagnose — explain the root cause to me before proposing any edit.
- Step 4: Fix — apply the minimal change that addresses the root cause.
- Step 5: Verify — run tests, confirm the symptom is gone and no regressions.
- Step 6: Protect — write a regression test if one doesn't already exist.

## Quality Gates
- Run the relevant test suite or type checks after every change. Report results before claiming done.
- When refactoring database schemas, always include the corresponding migration in the same change.
- Commit after each completed phase of a multi-step plan. Protects progress if we hit rate limits.
- For bugs: write a failing test first, then fix, then confirm green.
- Never claim work is complete without showing passing verification output.

## Token Efficiency
- Concise responses. No trailing summaries — I can read the diff.
- Don't read files you don't need. Don't explore broadly when the problem is specific.
- Suggest /compact when context exceeds 40%.
- Tool hierarchy: CLI commands first, API endpoints second, skills third, MCP only when nothing else fits. CLI uses 60-70% fewer tokens than MCP equivalents.
- No preambles ("Great question!", "I'd be happy to help"). No motivational filler. No emojis unless I use them first.
- Don't repeat back what I said. Don't summarize what you just did.

## Environment (Windows 11)
- Shell: bash (Git Bash). Use Unix syntax, forward slashes, /dev/null not NUL.
- Python: managed with uv. Use `uv run` to execute, `uv sync` to install.
- Node: npm or pnpm depending on project (check for lock file).
- Ports: Avoid Windows-reserved ports (especially 8090). Check availability before binding.
- Paths: Always verify working directory before build/setup commands. Wrong cwd is the #1 env failure.
- Config: Verify .env, local.properties, tsconfig.json exist where expected before running commands that depend on them.

## Self-Improvement
- When I correct your approach or point out a mistake, propose a specific addition to this project's CLAUDE.md that would prevent the same mistake in future. Present the proposed rule and wait for my approval before writing it.

## Communication
- Be direct. State what you found, what you'll do, and do it.
- When referencing code, include file_path:line_number.
- No emojis unless I do first. No motivational filler.

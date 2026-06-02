# Global Instructions

## About Me
- ICT Infrastructure Engineer building internal apps and personal projects, on Windows 11 (bash shell via Git Bash)
- Strong: networking, infrastructure, understanding how systems connect across the internet
- Growing: software architecture patterns, system design at scale, infra-as-code
- Goal: infra/architect roles — I want to build deep architectural intuition, not just working code
- Projects: Django monorepo (Shiploads), Shiploads website, Shiploads mobile app (Expo/React Native), MCP server (Python), Football webapp, SuppliesFixturesFirstAid fullstack
- Primary languages: TypeScript, Python, HTML/Django templates
- Tools: uv (Python), npm/pnpm (JS/TS), git, make, pytest

## When Explaining
- After non-trivial changes, briefly explain: architectural effects, tradeoffs, and why this approach over alternatives.
- Flag scalability implications — what works now but would break at scale, and why.
- Connect code decisions to operational impact — what this means for monitoring, debugging, and running in prod.
- Anchor new concepts to infra analogues I already know — I need reference points to fully appreciate the architecture.
- Keep explanations tight (2-4 lines). Don't over-explain what I already know from the infra side.

## Execution Style
- Execute inline and directly. Do NOT spawn subagents, nested skills, or brainstorming phases unless I explicitly ask.
- Show progress as you go. No invisible state-checking or skill-loading.
- If I give you a plan or spec file, follow it phase by phase. Don't re-plan or re-scope it.

## System Design First Principles
- Separation of concerns — each module/layer owns one responsibility.
- Single source of truth — data and config live in one canonical place.
- Fail fast — validate at boundaries, surface errors early, don't silently swallow.
- Idempotency — operations should be safe to retry without side effects.
- Least privilege — grant minimum access needed, especially for APIs and DB queries.
- Design for deletion — prefer small, removable pieces over deep coupling.

## Planning Threshold
- Single-file changes or isolated edits: implement directly. No plan needed.
- Multi-file changes or cross-cutting work: enter plan mode first. Present the plan, wait for my approval, then execute.
- If unclear, ask: "This touches N files across M areas — plan first or go direct?"
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
- When I reference something that exists ("there's a command that..."), ask me to identify it before assuming it doesn't exist or offering to build a replacement.

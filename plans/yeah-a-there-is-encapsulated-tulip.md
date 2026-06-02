# store-dashboard.js — Deduplicate, Refactor, Modularize

## Context

The store-dashboard extraction (commits `bf8a8b8`…`bbd039a` on `refactor/store-dashboard-extraction`) succeeded: the template went from 15.9k → 1.2k lines and the JS is in real static files. The next goal is to **shrink the code itself**, not just relocate it. Concretely:

- [CashOrderApp/static/js/store-dashboard/dashboard.js](CashOrderApp/static/js/store-dashboard/dashboard.js) is one 11,741-line file. Smaller, function-scoped modules will make navigation, code review, and future logic changes much easier.
- That file contains substantial duplication that was deliberately preserved during extraction:
  - 8 `display*Notes(WT)?` functions — 4 day/week pairs, ~785 lines total, near-clones.
  - 18 per-register state vars (`varianceDataJSONreg1..6`, `pettycashJSONreg1..6`, `returnsJSONreg1..6`) with 164 unrolled references.
  - 3 pairs of "live vs history" reconciliation/safe-float helpers (`getReconciliationJsonData` vs `…History`, ditto SafeFloat, ditto `checkStoreReconciliationRecords`) — 6 fns / ~280 lines, near-clones.
  - 165 `console.log` calls, most look like leftover debug instrumentation.

Out of scope for this round: the **submit-button reliability** work (boolean normalization, single `applyZreadButtonState()`, debug-logged transitions). That is a real logic change and stays in its own follow-up session.

Branch: keep working on `refactor/store-dashboard-extraction`. **One commit per sub-phase** so every change is independently bisectable / revertable. Smoke-test in the browser between phases.

## Approach

Six phases, each its own commit. Each phase ends with `python manage.py check` clean + a targeted browser smoke test before committing.

### Phase A — Modularize `dashboard.js` into 5 files (function moves, no logic change)

Now that the file is pure JS, a sibling split is just `sed` + a `<script src>` reorder — no Django-tag handling, no template surgery. The five files (matching the original plan's intent):

1. `dashboard-core.js` — globals (identity, dates, submit flags, per-register state, mastervalues, etc.), `csrftoken` + `$.ajaxSetup`, generic helpers (`showForm`, `getCookie`, `csrfSafeMethod`, `updateTotal`, `highlightNavItem`, `formatDateToActualDate`, `parseDateString`, `getFullDayName`, `disableInputs`, `highlightDefaultTab`, `disableFutureTabs`, `updateCurrentDayClass`, `getReconciliationJsonData[History]`, `getSafeFloatJsonData[History]`, `resetDataObjects`, `checkStoreReconciliationRecords[History]`, `handleExport`). Loads first.
2. `zread-calculations.js` — clearance/register-read/variance/cash-variance calc + highlighting, `toggleCashVarianceNotesTableDatabase`, `dynamicCashVarianceNotesShowOrDisableDatabase`, the `window.*` validators referenced at the original line ~5458 comment.
3. `zread-data-load.js` — `getStoredData`, `updateInputFields`, `openDay` (stays a real global — inline `onclick`), the tab-switch fetch logic, and the `getCurrentDateHistory` family.
4. `zread-submit.js` — `addEventListeners`, the first/second zread submit click handlers, weekly Z-Read fetch handlers.
5. `reports-modals.js` — `displayPettyCashNotes`, `displayReturnsNotes`, `displayVarianceNotes`, `displayCashVarianceNotes`, their `…WT` variants, `window.onclick = …` (modal close), and any other weekly-modal wiring.

Load order in the template (Phase 10-equivalent):
```
day-table-builder.js  (existing, before jQuery, builds the day-table DOM)
local-draft.js        (existing, before jQuery)
jQuery / SweetAlert2 / FileSaver (CDN)
storeDashboardConfig + StoreDashboard bootstrap (existing inline script)
dashboard-core.js
zread-calculations.js
zread-data-load.js
zread-submit.js       (must load after reports-modals so addEventListener('dblclick', displayXxxNotes) refs resolve)
reports-modals.js     ← actually load BEFORE zread-submit per the audit; swap order with line above
```

Reality check before committing: if any function is called at file-top-level (not just defined), the file that *defines* the callee must load first. `openDay(null, days[currentDayIndex])` currently runs late — move that line to the end of `zread-data-load.js` (after `openDay` is defined) so it executes after every dependency is loaded.

One commit per file: `A1: dashboard-core.js`, `A2: zread-calculations.js`, `A3: zread-data-load.js`, `A4: zread-submit.js`, `A5: reports-modals.js + load-order finalization`.

### Phase B — Dedup the `display*Notes(WT)?` pairs

One commit per type (4 commits): `B1 PettyCash`, `B2 Returns`, `B3 Variance`, `B4 CashVariance`. For each pair, diff the two functions, factor the difference into a `{ weekly: bool }` (or `mode: 'day'|'week'`) parameter, keep the original public names as thin wrappers if any inline handler depends on the exact name, otherwise replace both with one canonical function and update call sites. Estimated saving: 350–500 lines.

### Phase C — Dedup reconciliation / safe-float live vs history pairs

Three commits: `C1 getReconciliationJsonData(data, {history})`, `C2 getSafeFloatJsonData(data, {history})`, `C3 checkStoreReconciliationRecords(storeName, day, {history})`. Same diff/parameterize/replace pattern. Estimated saving: 120–150 lines.

### Phase D — Consolidate per-register state

Introduce three keyed containers in `dashboard-core.js`:
```js
var varianceDataJSON = { 1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{} };
var pettycashJSON    = { 1:[], 2:[], 3:[], 4:[], 5:[], 6:[] };
var returnsJSON      = { 1:[], 2:[], 3:[], 4:[], 5:[], 6:[] };
```
**Phase D is two commits.** `D1` is a *purely mechanical* rename of all 164 references: `returnsJSONreg3` → `returnsJSON[3]` etc., zero logic change, very easy to verify (page should look identical). `D2` then collapses the unrolled `if (!returnsJSONreg1) {…} if (!returnsJSONreg2) {…} …` ladders into `for (let r = 1; r <= 6; r++) {…}` loops. Saving: 100–150 lines, mostly from `D2`.

### Phase E — Dead code & console.log cleanup

Two commits.

`E1 — console.log triage`: of the 165 calls, keep only those that log on the **error path** (caught exceptions, server-error branches) or that the user uses for active diagnosis. Drop the rest (the `Print None json`, `Has first Submit`, `Returns: …`, etc. that fired on every page load during our smoke test). When in doubt, keep — this is the kind of thing where over-deletion bites later.

`E2 — stray tokens / obvious dead code`: the "stray `f`" token called out in the original extraction plan, any provably unreachable branches found during phases A–D, unused helpers. No speculative refactors.

### Phase F — Final verification

No code change. Full manual smoke test of the dashboard against the same checklist from the extraction plan's Phase 10: dashboard navigation, order-change submit, outstanding orders, previous orders, zread day-tab switching Mon–Sun, first clearance calc, second clearance calc, register-read calc, variance/note dialogs, first zread submit, second zread submit, safe float, banking reconciliation, weekly totals, Z-Read history, print/export. Console clean (only the extension noise we already identified).

## Critical files

- `CashOrderApp/static/js/store-dashboard/dashboard.js` — split in Phase A; gradually shrinks across B–E
- `CashOrderApp/static/js/store-dashboard/dashboard-core.js` — new in A1; receives most globals & helpers
- `CashOrderApp/static/js/store-dashboard/zread-calculations.js` — new in A2
- `CashOrderApp/static/js/store-dashboard/zread-data-load.js` — new in A3
- `CashOrderApp/static/js/store-dashboard/zread-submit.js` — new in A4
- `CashOrderApp/static/js/store-dashboard/reports-modals.js` — new in A5
- `CashOrderApp/templates/inventory/store-dashboard.html` — only the `<script src>` includes near end-of-body change (Phase A only)
- `CashOrderApp/static/js/store-dashboard/day-table-builder.js`, `local-draft.js` — untouched (already small + clean)

## Verification

Cumulative pass after Phases B/C/D/E:

1. `python manage.py check` — clean after every commit.
2. In a logged-in store browser session, hit every menu item: Order Change (enter values, watch totals update, submit), Outstanding Orders (load, ack/delivered actions), Previous Orders (load, export, PDF), Z-Read/Notes (every Mon–Sun tab — first clearance, second clearance, register read calculations, type into a red Returns/PettyCash/Variance cell and verify the note dialog opens, save notes, verify red→green transitions, first submit, second submit), Safe Float (load + submit), Banking Reconciliation (load + submit), Z-Read Weekly Total/Notes (double-click each note type — modals must show identical content to before), Z-Read History.
3. Browser console: zero `ReferenceError` / `TypeError` originating from any of our files (the existing extension noise — `tabs:outgoing.message.ready`, `lockdown-install.js`, `web-client-content-script.js` — is unrelated and stays).
4. `git diff <previous-commit>..HEAD --stat` after each phase — confirm only the intended files moved.
5. **Net code change**: target a reduction of ~1500–2000 lines off `dashboard.js`'s 11,741. Final tally reported in the Phase F commit message.

Rollback: every phase is its own commit on the branch. `git revert <sha>` for a single bad phase, or `git reset --hard <previous-sha>` to drop the in-flight phase entirely.

# Admin Status Frontend Implementation

## Context

The backend now supports admin status overrides on orders (auto-detected deleted JotForm submissions, manual flagging as duplicate/cancelled/other). The frontend needs to display these statuses, show detail in expanded rows, and provide UI to set/clear them.

## Files to Modify

- `src/lib/types.ts` — Add 6 new Submission fields, AdminStatus type, AdminStatusUpdate interface
- `src/lib/api.ts` — Add `updateAdminStatus()` method
- `src/components/StockAdminApp.tsx` — Display changes + action UI
- `src/app/globals.css` — Badge styles, muted row, detail section, action bar

---

## Phase 1: Types & API Client

**types.ts:**
- Add `AdminStatus = "not_found" | "duplicate" | "cancelled" | "other"`
- Add `AdminStatusUpdate` interface: `{ adminStatus: AdminStatus | null; reason?: string }`
- Extend `Submission` with 6 fields: `adminStatus`, `adminStatusReason`, `adminStatusAt`, `adminStatusBy`, `effectiveStatus`, `doNotServe`
- Keep `status: OrderStatus` as-is — use `effectiveStatus` for display with fallback

**api.ts:**
- Import `AdminStatusUpdate`
- Add `updateAdminStatus(submissionId, body)` → `PATCH /api/orders/{id}/admin-status`

**Commit point: types and API ready, app compiles, no UI changes.**

---

## Phase 2: Display Changes (Read-Only UI)

**StockAdminApp.tsx:**
- Add `ADMIN_STATUS_BADGE_CLASS` and `ADMIN_STATUS_LABEL` mappings
- Add `statusBadgeClass()` helper: checks ORDER_STATUS → ADMIN_STATUS → fallback
- Orders table row: add `do-not-serve-row` class when `doNotServe` is true
- Status cell: when `doNotServe`, show admin status badge prominently + original status with strikethrough; otherwise show status as before
- Expanded row: show admin status detail block (status, reason, set by, timestamp) above LineItemsTable when `adminStatus` is set

**globals.css:**
- `.badge-admin-not-found` — red (system-detected)
- `.badge-admin-duplicate` — amber
- `.badge-admin-cancelled` — red
- `.badge-admin-other` — neutral/gray
- `.badge-struck` — strikethrough + opacity for overridden status
- `.do-not-serve-row td` — opacity: 0.55, hover 0.75
- `.admin-status-detail` — surface2 background, flex rows for metadata

**Commit point: admin statuses visible in table and expanded rows.**

---

## Phase 3: Admin Actions (Write Operations)

**StockAdminApp.tsx:**
- Add state for admin action modal in `OrdersScreen`
- Action buttons in expanded row: "Mark as: Duplicate | Cancelled | Other" (when no admin status) or "Clear admin status" (when set)
- `not_found` excluded from manual actions — system-only
- Confirmation modal with optional reason textarea (reuse `confirm-modal` pattern from SkewedStockModal)
- `submitAdminAction()` calls `api.updateAdminStatus()`, updates order in-place in local state
- `e.stopPropagation()` on action buttons to prevent row toggle

**globals.css:**
- `.admin-actions` — flex row with gap
- `.admin-reason-field` / `.admin-reason-input` — textarea styling

**Commit point: full feature complete.**

---

## Key Decisions

1. **Keep `status: OrderStatus`** — don't widen to string. `effectiveStatus` handles display. `ORDER_STATUS_BADGE_CLASS` stays type-safe.
2. **Actions in expanded row** — avoids crowding table cells and conflicting with click-to-expand.
3. **Reuse `confirm-modal` pattern** — consistent with existing SkewedStockModal UI.
4. **`not_found` is system-only** — users can see it and clear it, but can't manually set it.
5. **In-place state update** after PATCH — avoids full refetch, keeps UI responsive.
6. **Opacity for muted rows** — works universally with all existing badge/text colors.

## Verification

- `npm run build` after each phase to confirm no type errors
- Manual test: load orders page, verify admin status badges render
- Manual test: expand a row, verify detail section and action buttons
- Manual test: set an admin status, verify modal, confirm, check row updates
- Manual test: clear an admin status, verify row returns to normal

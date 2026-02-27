# NoteShift — Licensing / Paywall Spec (Add Later)

Status: **Deferred** (post-MVP)

Goal: enable a paid tier for a **local CLI** without changing the core UX or forcing a hosted workflow.

This spec is designed so we can:
- ship an MVP with **no licensing**, then
- add licensing later with minimal refactor.

---

## 1) Non-goals
- DRM. We are not trying to make piracy impossible.
- Continuous online enforcement.
- Collecting/exporting user data.

---

## 2) Paywall model options (ranked)

### Option A — Signed license file (recommended)
**Model:** user buys a license key → receives a signed license payload → CLI verifies signature locally.

- No server required at runtime.
- Works offline.
- Best fit for migration tools.

### Option B — Signed license + periodic online validation
Adds revocation, seat enforcement, activation limits.

### Option C — Separate binaries (free core vs pro)
Operationally heavier; only worth it if we open-source core.

### Option D — Hosted conversion
Strong enforcement but introduces privacy + infra + security scope.

We will implement **Option A** first.

---

## 3) Product & UX requirements

### Commands
- `noteshift license status`
  - prints: licensed/unlicensed, tier, expiry (if any), seats (if any)

- `noteshift license activate <license_string_or_path>`
  - accepts either:
    - a pasted string, or
    - a path to a `noteshift.license` file
  - writes to a local config directory

- `noteshift license deactivate` *(optional)*
  - deletes local license file

### Storage
- Linux/macOS: `~/.config/noteshift/license.json`
- Windows: `%APPDATA%\\noteshift\\license.json`

Do **not** store the raw payment token.

### Failure mode
- Unlicensed users can run free features.
- When a Pro-only feature is invoked:
  - error message must be explicit and actionable:
    - what feature is locked
    - how to purchase
    - how to activate

---

## 4) Technical design

### 4.1 License payload format
Use JSON (human-readable) + signature.

#### Payload (example)
```json
{
  "product": "noteshift",
  "license_id": "lic_01H...",
  "issued_at": "2026-02-27T00:00:00Z",
  "tier": "personal",
  "expires_at": null,
  "user": {
    "email": "user@example.com"
  },
  "entitlements": {
    "resume": true,
    "db_index_pages": true,
    "reconciliation_report": true,
    "max_pages": null,
    "max_db_rows": null
  },
  "machine": {
    "binding": "optional",
    "fingerprint": null
  },
  "signature": {
    "alg": "ed25519",
    "kid": "noteshift-ed25519-2026-01",
    "sig": "base64..."
  }
}
```

Signing rules:
- Signature covers the canonical JSON of the payload **without** the `signature` field.
- Use Ed25519.
- CLI ships with one or more public keys (`kid` → pubkey).

### 4.2 Canonicalization
To avoid signature mismatch:
- Serialize with sorted keys.
- UTF-8.
- No pretty-print required, but canonicalize prior to verify.

### 4.3 License verification API (internal)
Create a single internal module, e.g. `noteshift.license`:

- `load_license() -> License | None`
- `verify_license(license: License) -> VerificationResult`
- `require_entitlement(name: str)`

### 4.4 Entitlement gates
Implement gates at the **feature boundary**, not scattered.

Recommended pattern:
- Central feature registry:
  - `Feature.RESUME_EXPORT`
  - `Feature.DB_INDEX_PAGES`
  - `Feature.RECONCILIATION_REPORT`

Then gate CLI flags/routes:
- `--resume` invokes `require_entitlement(RESUME_EXPORT)` if we decide resume is paid
- `--db-index-pages` invokes `require_entitlement(DB_INDEX_PAGES)`

Avoid gating deep inside the exporter; keep exporter pure and testable.

### 4.5 Free vs paid mapping (initial)
**Free** (MVP-friendly):
- small export limits
- basic pages → markdown

**Paid**:
- robust toggle/indentation fidelity guarantees
- attachment handling + manifest
- internal link rewriting
- database usability layer (index pages)
- resumable + reconciliation report

Note: we may decide to keep **resume** free because it’s a reliability requirement. If so, gate other features instead.

---

## 5) What we must do now (MVP) to not block licensing later

### 5.1 Stable CLI surface
- Use a consistent command structure (`noteshift export`, `noteshift doctor`, etc.).
- Avoid breaking flag names.

### 5.2 Feature boundaries
Structure code so major capabilities are discrete modules:
- exporter core
- link rewriter
- attachments downloader
- database export
- report generator

This makes it easy to gate modules later.

### 5.3 Deterministic config path
Add a config directory abstraction now (even if unused), so license storage drops in cleanly later.

### 5.4 No irreversible architectural commitments
Avoid:
- baking pricing/tier logic into the core exporter
- coupling “pro” to a hosted service

---

## 6) Operational (later)

### Issuance
- Checkout provider: Stripe / Lemon Squeezy / Paddle.
- After payment: deliver a license string/file (email + download).

### Key rotation
- Support multiple `kid` public keys in the binary.
- License includes `kid`.

### Support tooling
- A small internal tool to generate/revoke licenses (offline is fine initially).

---

## 7) Test plan
- Valid signed license → unlocks entitlements.
- Tampered license → fails verification.
- Missing license → Pro features blocked with clear message.
- Multiple public keys → correct key chosen by `kid`.

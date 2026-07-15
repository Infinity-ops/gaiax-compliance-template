# Policy Inventory (with evidence)

For each policy category your service actually has a real answer to, fill
in a row. **Leave out categories that genuinely don't apply** — don't
invent a cross-border-transfer policy for a service that only ever runs in
one country. The point of this document is to only publish claims you can
back up.

The `Evidence` column is the important addition in v2: a policy claim
without a pointer to something verifiable is a promise, not compliance
evidence. "Trust me" isn't a Gaia-X policy; "enforced by `CleanupPolicy`
table, checked nightly by `services/scheduler.py`" is.

| Policy | Claim | Evidence (what proves it, concretely) |
|---|---|---|
| Retention | e.g. "Configurable per-record, default 30 days" | e.g. `CleanupPolicy` DB table + `services/cleanup.py` nightly job |
| Deletion | e.g. "Available on request, effective immediately" | e.g. `DELETE /api/jobs/{id}` endpoint, cascades to storage |
| Processing location | e.g. "Germany only" | e.g. Infrastructure contract / hosting provider's DC location |
| Sharing with third parties | e.g. "None" | e.g. Code review confirms no external API calls with customer data |
| Cross-border transfer | (only if applicable) | |
| Consent | (only if applicable) | |
| Audit logging | (only if applicable) | |
| Access control | e.g. "Role-based, per organization" | e.g. `auth.py` role checks |

Categories not in this table but that Gaia-X ecosystems sometimes require:
purpose limitation, export policy, versioning policy. Add rows as needed —
this table isn't exhaustive, it's a starting checklist.

Once filled in, transcribe each row into `gaiax.config.yaml`'s `policies:`
map — each policy becomes a named entry with `claim` and `evidence` fields,
rather than v1's flat, evidence-free block.

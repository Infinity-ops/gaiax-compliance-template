# Versioning & Credential Lifecycle

v1 had no answer for "what happens on the next release." v2's
`gaiax.config.yaml` has a `versioning:` block; here's what it means in
practice.

## When you bump `service_offerings[].version`

Two strategies, set via `versioning.strategy`:

- **`additive` (default).** The old version's credential stays hosted at
  its existing URL (`service-offering-<id>.json` doesn't get overwritten in
  place — see note below) and stays valid. Consumers who cached a reference
  to the old version aren't broken. Use this unless you have a specific
  reason not to; Gaia-X consumers may hold a reference to your Service
  Offering for a while before re-checking the catalog.
- **`replace`.** The old credential is explicitly revoked. Only do this for
  a genuine breaking change (e.g. the service now operates under different
  legal terms, or a Data Resource it used to produce no longer exists) —
  and give consumers the `deprecation_notice_days` warning window first.

**Practical note on the `additive` strategy:** `build_credentials.py`
currently overwrites `service-offering-<id>.json` on every run — it does
not itself keep old versions around. If you want true additive versioning,
either encode the version in the filename (e.g.
`service-offering-primary-v1.0.0.json`) before regenerating, or keep old
signed files in version control / a separate archive path. This template
gives you the config flag and the policy; wiring actual multi-version
file retention is left to you since it depends on how your CI/deployment
publishes `.well-known/`.

## Credential expiry and renewal

Gaia-X credentials don't have a single hardcoded lifetime — how long a
Compliance Credential remains trusted is a GXDCH/ecosystem policy question,
and has changed across Gaia-X releases. Treat the Compliance Credential you
get back from `submit_compliance.py` as something to re-request
periodically rather than something you generate once and forget — see
`.github/workflows/continuous-compliance.yml`, which re-checks on a
schedule rather than only on `git push`.

## Revocation

If your organization's registration lapses, your domain changes, or a
policy claim stops being true, don't just stop hosting the credential —
that leaves a stale, still-technically-fetchable document making a claim
that's no longer accurate. Explicitly publish a revocation (check current
GXDCH docs for the mechanism, as this is one of the areas still evolving
release to release) rather than relying on link rot.

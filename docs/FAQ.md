# FAQ

**Q: The endpoint URLs in `gaiax.config.yaml` return 404 / schema errors.**
Gaia-X's tooling and endpoint URLs change between releases (the ecosystem is
mid-transition from the "Tagus" architecture to "Danube" as of late 2025/2026).
The URLs in this template are the current publicly-documented lab/staging and
production endpoints as of when this template was written. Check
`docs.gaia-x.eu` and the Gaia-X Wizard (`https://wizard.lab.gaia-x.eu/`) for
current values before assuming the template is broken — update
`gaiax.config.yaml`'s `gxdch:` section and open a PR if they've moved.

**Q: Can I skip the GXDCH and just self-sign everything?**
You can generate and host self-signed credentials without ever calling
`submit_compliance.py` — nothing stops you. But "Gaia-X compliant" is a
claim about a GXDCH-issued Compliance Credential specifically. Self-signed,
unvalidated credentials are Gaia-X-*shaped* JSON, not a compliance claim.
Don't describe your service as compliant until step 6 actually succeeds.

**Q: Do I need a real EV/eIDAS certificate to test this?**
No — set `environment: staging` in the config. The `*.lab.gaia-x.eu`
services explicitly accept Let's Encrypt certificates for testing. Only
switch to `production` once you're ready to notarize a real registration
number and want a Compliance Credential that's actually recognized outside
test environments.

**Q: My `policy.json` retention field doesn't match what my app actually
does — is that a problem?**
Yes, treat it as a real bug, not a formatting detail. A published Gaia-X
policy is a trust claim; if it drifts from what your system enforces, you're
misrepresenting your service to anyone who relies on the catalog listing.
Prefer wiring the field to a live query (see the `api/*_example` files)
over a static number whenever your retention/sharing rules are configurable.

**Q: Can I use this for a non-EU / non-German entity?**
Yes — `registration_type` supports `vatID`, `leiCode`, `EUID`, and `EORI`,
which cover most jurisdictions with a Gaia-X-recognized identifier. If your
entity has none of these, check the current Gaia-X Trust Framework
Participant shape for what identifiers are accepted — it does get extended.

**Q: Something in the JSON-LD `@context` / mandatory fields doesn't match
what the Compliance Service expects.**
Query the Gaia-X Registry's trusted-shape endpoint for the currently
mandatory attributes of the credential type you're building
(`/v1/api/trusted-shape-registry/v1/shapes`) — Gaia-X versions its shapes,
and this template targets one point-in-time snapshot of them.

**Q: `scripts/build_credentials.py` fails with a `JsonLdError` about
"loading remote context failed."**
Signing a credential requires normalizing it via JSON-LD, which resolves
the `@context` URL over the network (it's not just a string — it's fetched
and parsed). Run this from an environment with outbound HTTPS access to
`registry.lab.gaia-x.eu` (or `registry.gaia-x.eu` in production) — a
sandboxed CI runner with restricted egress will fail here even though
nothing in your config is wrong.

**Q: Do I need to re-run the whole flow if I only change my service
description?**
No — only `build_credentials.py` (step 4) needs to re-run, since it's the
one that renders and re-signs the Service Offering. Your DID, keys, and LRN
credential (steps 2–3) don't need to change unless your identity or
registration number changes.

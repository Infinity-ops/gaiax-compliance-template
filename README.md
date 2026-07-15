# gaiax-compliance-template

A framework-agnostic starter kit for making **any** application or service
Gaia-X compliant: business/repository assessment, an explicit business →
Gaia-X Information Model mapping, evidence-based policy claims, Self
Descriptions, Verifiable Credentials, DID:web identity, GXDCH compliance
submission, and a small metadata API you drop into your existing backend.

This is **not** a Gaia-X SDK and it doesn't touch your business logic. It
produces and serves the declarative artifacts Gaia-X requires, scripts the
credential-signing workflow, and — as of v2 — forces you to answer the
business questions Gaia-X actually cares about before any JSON-LD gets
generated.

> Gaia-X is mid-transition to a new architecture (the "Danube" release). The
> endpoints wired up here target the current public Tagus-era GXDCH
> lab/staging services. Before submitting anything to **production**, check
> `docs.gaia-x.eu` for current endpoint URLs — see `docs/FAQ.md`.

## What's new in v2

v1 went straight from a flat config file to JSON-LD. A Gaia-X compliance
review of v1 (see `CHANGELOG.md` for the full critique) correctly flagged
that this skipped the actual hard part of Gaia-X — deciding what your
business capability, provider, and data assets *are* — and that a single
flat config couldn't represent Gaia-X's richer entity model. v2 addresses
this:

- **Phase 0 assessment** (`docs/PHASE_0_ASSESSMENT.md` + `docs/templates/`)
  — five short fillable documents you complete *before* touching config,
  so the config becomes a transcription of decisions already made, not
  where you make them.
- **Explicit Information Model mapping** (`gaiax/mapping.yaml`) — a
  reviewable record of which business object maps to which Gaia-X ontology
  class, checked by `scripts/validate_local.py` rather than living only in
  a developer's head.
- **Multiple Service Offerings and Data Resources** — `gaiax.config.yaml`
  now supports a list of offerings and a separate `gx:DataResource` entity
  for datasets/reports your service produces, instead of one flattened
  block.
- **Evidence-based policies** — every policy is a `claim` + `evidence` pair.
  `scripts/validate_local.py` fails the build if a claim has no evidence
  pointer — a policy nobody can verify isn't compliance, it's a promise.
- **Versioning strategy** (`docs/VERSIONING.md`) and a **continuous
  compliance** scheduled CI check
  (`.github/workflows/continuous-compliance.yml`) that re-verifies your
  hosted credentials weekly instead of treating compliance as a one-time
  event.
- **Architecture diagram** (`docs/ARCHITECTURE.md`) showing the revised
  flow and the trust boundary — what stays inside your org vs. what's
  public vs. what the GXDCH sees.

## What's in here

```
docs/PHASE_0_ASSESSMENT.md      ← start here, before any config
docs/templates/                 ← fillable inventory documents for Phase 0
gaiax/mapping.yaml               ← explicit business → Gaia-X class mapping
gaiax.config.yaml                ← single source of truth for identity/services/policies
gaiax/templates/                 ← JSON-LD credential templates
scripts/                         ← key generation, DID setup, signing, submission, validation
api/                              ← reference metadata endpoints (FastAPI, Express, Flask)
.well-known/                     ← files you host at your domain root
.github/workflows/                ← PR validation + scheduled continuous-compliance check
docs/ARCHITECTURE.md, docs/VERSIONING.md, docs/FAQ.md, docs/QUICKSTART.md
```

## Quickstart

1. **Do Phase 0 first.** Read `docs/PHASE_0_ASSESSMENT.md`, fill in the five
   documents in `docs/templates/`. This is the part that actually requires
   thought — everything after this is mechanical.
2. Fill in `gaiax/mapping.yaml`, then `gaiax.config.yaml`, transcribing the
   decisions from step 1.
3. `pip install -r requirements.txt`
4. `python scripts/validate_local.py` — must pass before continuing. Fails
   on unfilled placeholders, policies without evidence, or mapping
   inconsistencies.
5. `python scripts/generate_keys.py && python scripts/generate_did.py` →
   host `.well-known/did.json` + your TLS cert chain at your real domain.
6. `python scripts/request_lrn.py` → notarizes your registration number via
   the GXDCH Notarization API.
7. `python scripts/build_credentials.py` → generates and signs Participant,
   Terms & Conditions, one Service Offering per configured offering, and
   one Data Resource per configured resource.
8. Redeploy `.well-known/`, then `python scripts/submit_compliance.py` →
   submits to the GXDCH Compliance Service, prints the resulting Compliance
   Credential or validation errors.
9. Drop `api/fastapi_example.py` (or Flask/Express) into your service.

Full walkthrough: `docs/QUICKSTART.md`. Full architecture and trust-boundary
diagrams: `docs/ARCHITECTURE.md`.

## Design principles

- **Business decisions before config edits.** Phase 0 exists so nobody
  fills in a Service Offering before deciding what their service offering
  actually is.
- **Config-driven, not code-driven.** Change your legal name or retention
  policy in YAML, not Python.
- **Claims need evidence.** A policy claim with no pointer to something
  verifiable (a config value, a cron job, a DB table) fails validation.
- **Static claims stay close to the truth.** The API reference examples
  show merging a static policy with a live database read, so published
  claims can't silently drift from what your system enforces.
- **Never fabricate identity.** Every field requiring a real legal fact is
  an obvious `REPLACE_ME`. The build refuses to proceed with any left.
- **Staging first.** Every script defaults to `*.lab.gaia-x.eu`. Production
  is one explicit config flag away.
- **Compliance isn't a one-time event.** A scheduled CI job re-checks your
  hosted credentials are still live and well-formed.

## License

MIT — see `LICENSE`. Use this for any application, commercial or not.

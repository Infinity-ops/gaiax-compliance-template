# gaiax-compliance-template

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Lint](https://github.com/Infinity-ops/gaiax-compliance-template/actions/workflows/lint.yml/badge.svg)
![Status](https://img.shields.io/badge/status-community%20preview-orange.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

**A starter kit that turns "we need to be Gaia-X compliant" from a
six-week research project into a checklist.**

Gaia-X's own docs are correct, thorough, and genuinely hard to turn into
working code — most teams either burn weeks reverse-engineering JSON-LD
signing and credential ordering, or hire a consultant. This repo is the
distilled version: fill in five short documents about your business, run
eight scripts in order, end up with a signed Gaia-X Compliance Credential
for *any* application, in any language, on your own infrastructure.

Not affiliated with or endorsed by Gaia-X AISBL. "Gaia-X" is a trademark of
the Gaia-X Association — this is an independent, community-built
implementation of their public specifications.

## What you actually get

- 📋 **Phase 0 assessment** — five plain-language documents that force the
  real decisions (who's the legal entity, what's the service, what's the
  evidence for each policy) before any YAML gets touched
- 🧩 **Explicit Information Model mapping** — a reviewable file linking
  every business object to its Gaia-X ontology class, not just tribal
  knowledge in one developer's head
- 🔐 **Real signing, not a mock** — proper JSON-LD (URDNA2015) normalization
  and detached JWS, the same mechanism Gaia-X's own tooling uses
- ✅ **Evidence-based policies** — a claim with no pointer to something
  verifiable fails validation, on purpose
- 🔁 **Continuous compliance** — a scheduled CI job that catches credential
  rot before a real consumer does
- 🧱 **Framework-agnostic** — FastAPI, Flask, and Express reference
  endpoints included; the pipeline itself doesn't care what you're running

## Status — read this before you trust it blindly

Local generation, signing, and validation are tested end-to-end — the
config → mapping → JSON-LD → signed-credential pipeline runs cleanly
against both empty and fully-populated configs.

The GXDCH round-trip has been tested live against staging, and that testing
already caught and fixed a real bug: a `#` in the LRN `vcid` parameter was
being sent unencoded, silently truncated by any URL parser as a fragment.
`scripts/request_lrn.py` now percent-encodes it correctly. If you hit
something else against a live GXDCH endpoint, **open an issue** — that's
how this gets from "works for us" to "verified for everyone."

> Gaia-X is mid-transition to a new architecture (the "Danube" release).
> Endpoints here target the current Tagus-era GXDCH lab/staging services —
> check `docs.gaia-x.eu` before pointing anything at production. Details in
> `docs/FAQ.md`.

## 60-second map of the repo

```
docs/PHASE_0_ASSESSMENT.md   → start here, before any config
docs/templates/              → the 5 fillable inventory docs for Phase 0
gaiax/mapping.yaml           → business object → Gaia-X ontology class
gaiax.config.yaml            → single source of truth, everything else derives from this
scripts/                     → keys → DID → notarize → build → submit, in order
api/                         → drop-in metadata endpoints (FastAPI / Flask / Express)
.github/workflows/           → PR validation + weekly continuous-compliance check
docs/                        → architecture, versioning, FAQ, full walkthrough
```

## Quickstart

```bash
pip install -r requirements.txt
```

| # | Command | What it does |
|---|---|---|
| 1 | fill `docs/templates/*.md` | Answer the business questions, in plain language — see `docs/PHASE_0_ASSESSMENT.md` |
| 2 | fill `gaiax/mapping.yaml`, then `gaiax.config.yaml` | Transcribe step 1's answers — mechanical, not creative |
| 3 | `python scripts/validate_local.py` | Must pass. Catches placeholders, missing evidence, broken references |
| 4 | `python scripts/generate_keys.py && python scripts/generate_did.py` | Creates your keypair + `did:web` identity → deploy `.well-known/` to your domain |
| 5 | `python scripts/request_lrn.py` | Notarizes your VAT/LEI/EUID/EORI against the real registry via GXDCH |
| 6 | `python scripts/build_credentials.py` | Signs Participant, T&Cs, every Service Offering + Data Resource |
| 7 | redeploy `.well-known/`, then `python scripts/submit_compliance.py` | Submits to the GXDCH Compliance Service → your Compliance Credential |
| 8 | mount `api/fastapi_example.py` (or Flask/Express) | Serves it all live, with a pattern for keeping policy claims honest against your real DB |

Full walkthrough with checkpoints: `docs/HOW_TO_USE_THIS_REPO.md`.
Architecture + trust-boundary diagrams: `docs/ARCHITECTURE.md`.

## Why it's built this way

| Principle | In practice |
|---|---|
| Business before config | Phase 0 exists so nobody writes a Service Offering before deciding what it *is* |
| Config-driven | Change your legal name or retention policy in YAML, never Python |
| Claims need evidence | No verifiable pointer → the build fails, deliberately |
| Static claims stay honest | Reference API merges a static policy with a live DB read, so publications can't quietly drift from reality |
| Staging first | Production requires an explicit flag flip — nobody accidentally notarizes a real VAT ID against a test service |
| Compliance isn't a one-time event | Weekly CI re-checks your hosted credentials are still live |

## Contributing

Issues and PRs welcome — especially real GXDCH submission reports (see
Status), schema-drift fixes as Gaia-X evolves, and framework examples
beyond the three included. Check `CHANGELOG.md` before proposing a
restructure — a few choices (one config file instead of five, for example)
were deliberate tradeoffs made after an external compliance review, not
oversights.

## License

MIT — see `LICENSE`. Use it for anything, commercial or not.

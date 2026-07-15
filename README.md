# gaiax-compliance-template

A framework-agnostic starter kit for making **any** application or service
Gaia-X compliant: Self-Descriptions, Verifiable Credentials, DID:web identity,
GXDCH compliance submission, and a small metadata API you drop into your
existing backend.

This is **not** a Gaia-X SDK and it doesn't touch your business logic. It only
produces and serves the declarative artifacts Gaia-X requires, and scripts the
credential-signing workflow so you don't hand-roll JOSE/JSON-LD signing
yourself.

> Gaia-X is mid-transition to a new architecture (the "Danube" release). The
> endpoints wired up here target the current public Tagus-era GXDCH
> lab/staging services. Before submitting anything to **production**, check
> `docs.gaia-x.eu` for current endpoint URLs — see `docs/FAQ.md`.

## What's in here

```
gaiax.config.yaml          ← the one file you actually edit first
gaiax/templates/           ← JSON-LD credential templates (placeholders only)
scripts/                   ← key generation, DID setup, signing, submission
api/                       ← reference metadata endpoints (FastAPI, Express, Flask)
.well-known/               ← files you host at your domain root
.github/workflows/         ← CI that catches config/placeholder drift
docs/                      ← quickstart, architecture notes, FAQ
```

## Quickstart

1. Fork/clone this repo, or copy `gaiax/`, `scripts/`, and one `api/*` file
   into your existing project.
2. Fill in `gaiax.config.yaml` — the single source of truth every script and
   template reads from.
3. `pip install -r requirements.txt`
4. `python scripts/generate_keys.py` → creates `keys/private.pem` +
   `keys/public.pem`. **Never commit `keys/private.pem`.**
5. `python scripts/generate_did.py` → creates `.well-known/did.json`. Host
   this file, `.well-known/x509CertificateChain.pem` (your TLS cert chain),
   and your public key at your real domain over HTTPS.
6. `python scripts/request_lrn.py` → notarizes your VAT/EUID/LEI number
   against the GXDCH Notarization API. This is the one credential you don't
   self-sign.
7. `python scripts/build_credentials.py` → generates and self-signs your
   Participant, Terms & Conditions, and Service Offering credentials from
   the config + templates.
8. `python scripts/submit_compliance.py` → bundles everything into a
   Verifiable Presentation and submits it to the GXDCH Compliance Service.
   Prints the resulting Gaia-X Compliance VC or the validation errors.
9. Drop `api/fastapi_example.py` (or the Express/Flask equivalent) into your
   service so it exposes `/gaia-x/self-description`, `/gaia-x/policy`, and
   `/gaia-x/compliance-credential` for consumers.

Full walkthrough with explanations of each artifact: `docs/QUICKSTART.md`.

## Design principles

- **Config-driven, not code-driven.** Nobody should have to write Python to
  change their legal name or retention policy — edit `gaiax.config.yaml`.
- **Static claims stay close to the truth.** The API reference examples show
  how to merge static policy text with a live read from your own database
  (e.g. actual retention rules), so published claims can't silently drift
  from what your system enforces. Don't ship a hardcoded policy blob if your
  service already tracks this dynamically — wire the endpoint to your DB.
- **Never fabricate identity.** Every template field that requires a real
  legal/registration fact is left as an obvious `REPLACE_ME` placeholder.
  `scripts/validate_local.py` fails the build if any placeholder remains.
- **Staging first.** Every script defaults to the Gaia-X `*.lab.gaia-x.eu`
  environment. Switching to production is one config flag away, deliberately,
  so nobody accidentally notarizes a real VAT ID against a test service.

## License

MIT — see `LICENSE`. Use this for any application, commercial or not.

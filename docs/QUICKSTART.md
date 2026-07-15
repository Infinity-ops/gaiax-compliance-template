# Quickstart — full walkthrough

This expands each step of the README quickstart with what's actually
happening and why it's ordered this way.

## 0. Prerequisites (do these before touching the repo)

- **A real legal entity** to be the Gaia-X Participant, with a VAT ID, LEI,
  EUID, or EORI number. This is an organizational decision — pick the entity
  that will actually stand behind the compliance claim.
- **A domain you control** with HTTPS. Gaia-X identity is domain-anchored
  (`did:web:yourdomain.com`); there is no way to get a Gaia-X identity
  without hosting something publicly.
- **A TLS certificate.** For `environment: staging` in `gaiax.config.yaml`,
  a free Let's Encrypt cert is accepted by the `*.lab.gaia-x.eu` services.
  For `environment: production`, you need a certificate from a recognized
  Trust Anchor (eIDAS-qualified or EV SSL) — plain Let's Encrypt is rejected.

## 1. Fill in `gaiax.config.yaml`

Every `REPLACE_ME` has to go. `scripts/validate_local.py` will refuse to
proceed otherwise — this is deliberate, so nobody accidentally notarizes a
placeholder or publishes a fabricated retention policy.

Pay particular attention to `policy.retention_days`: if your application
already has per-record or configurable retention (a cleanup job, a settings
table, an admin toggle), leave it `null` and instead wire
`get_live_retention_rules()` in your `api/*_example` file to your real data.
A hardcoded number here becomes a false statement the moment someone changes
a setting in your app without touching this repo.

## 2. Keys and DID

```
python scripts/generate_keys.py
python scripts/generate_did.py
```
This writes `keys/private.pem` (never commit this — it's in `.gitignore`
already) and `.well-known/did.json`. Deploy the entire `.well-known/`
directory to your domain's web root, alongside your certificate chain at
`.well-known/x509CertificateChain.pem`. Your identity becomes resolvable at
`https://yourdomain.com/.well-known/did.json` — there's no separate
registration call for the DID itself, Gaia-X just fetches this URL.

## 3. Legal Registration Number (the one credential you don't sign yourself)

```
python scripts/request_lrn.py
```
This posts your registration number to the GXDCH Notarization API, which
checks it against the real business register (e.g. EU VIES for VAT IDs) and
signs the resulting credential itself. You're the *subject*, not the
*issuer*, of this one credential — that's what makes it trustworthy to
someone who has never met you.

## 4. Build and self-sign your remaining credentials

```
python scripts/build_credentials.py
```
This fetches the mandatory Gaia-X Terms & Conditions text live from the
GXDCH registry (so you're never signing a stale copy), renders your
Participant and Service Offering templates from the config, and signs all
three with your private key using the real Gaia-X signing method: JSON-LD
normalization (URDNA2015) + a detached JSON Web Signature. Re-run this any
time you change `gaiax.config.yaml`.

## 5. Deploy `.well-known/` again

The Compliance Service in the next step verifies your credentials by
fetching their public URLs — not by trusting whatever you have locally. If
you generated new signed files in step 4, redeploy `.well-known/` before
continuing.

## 6. Submit for compliance

```
python scripts/submit_compliance.py
```
This builds a Verifiable Presentation referencing your four public
credential URLs and posts it to the GXDCH Compliance Service. A failure
here almost always means one of: the files aren't actually reachable yet at
those URLs, a field doesn't match the current GXDCH schema (schemas do
change between Gaia-X releases — check the registry's
`/trusted-shape-registry/v1/shapes` endpoint for the current mandatory
fields), or you rebuilt credentials in step 4 but forgot to redeploy.

On success you get back a signed Compliance Credential — save and host it
too, since it's the actual artifact that proves compliance to anyone
consuming your service.

## 7. Wire up the metadata API

Mount `api/fastapi_example.py`, `api/flask_example.py`, or
`api/express_example.js` into your existing app. These serve the generated
`.well-known/` files as live JSON endpoints, and the `/policy` route
demonstrates merging the static claim with a live database read — copy that
pattern for anything your app already tracks dynamically.

## 8. Catalog registration (beyond this template's scope)

Once you hold a valid Compliance Credential, publishing to a Federated
Catalogue is ecosystem-specific — which catalogue you register with (Gaia-X
Federated Catalogue, a domain-specific data space like a mobility or
agriculture data space, Pontus-X, Catena-X, etc.) determines the exact
registration mechanism. Check that ecosystem's onboarding docs once you get
here; this template intentionally stops at "you are compliant," since what
you do with that credential is a business decision, not a technical one.

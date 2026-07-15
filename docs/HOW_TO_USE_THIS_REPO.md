# How to Use This Repo — Full Guide

Two parts: **(A)** what your application/organization needs to have in
place before you touch this repo at all, and **(B)** the exact sequence of
steps and commands once you start. Skipping part A is the single most
common reason people get stuck halfway through part B.

---

## Part A — Checkpoints your app/org needs BEFORE starting

Think of this as a readiness gate. If you can't check a box, stop and
resolve it first — every script downstream assumes these are already true,
and will fail (sometimes confusingly) if they aren't.

### A1. Legal / organizational readiness

| Checkpoint | Why it's required | If missing |
|---|---|---|
| ☐ A real legal entity identified as the Gaia-X Participant | Gaia-X identity is tied to one legal entity, not "the project" or "the app" | Decide this *before* filling config — can't be split later without re-notarizing |
| ☐ A registration number for that entity (VAT ID, LEI, EUID, or EORI) | Required for `request_lrn.py` to notarize against a real business register | Get this from your entity's registration documents; can't be fabricated |
| ☐ Someone with authority to answer data-governance questions (retention, deletion, sharing) | Feeds the evidence-based policy section — needs real answers, not guesses | Get 30 minutes with whoever owns this (often not the developer) |

### A2. Technical readiness

| Checkpoint | Why it's required | If missing |
|---|---|---|
| ☐ A domain you control, with HTTPS | Your Gaia-X identity is `did:web:yourdomain.com` — no domain, no identity | Buy/use any domain you control; a subdomain is fine |
| ☐ Ability to host static files at `https://yourdomain.com/.well-known/` | This is where every generated credential must be publicly reachable | Any static hosting works (Nginx, S3+CDN, GitHub Pages, Vercel, etc.) |
| ☐ A TLS certificate for that domain | Staging accepts Let's Encrypt; production needs eIDAS/EV | Let's Encrypt is free and enough to start (`environment: staging`) |
| ☐ Python 3.9+ available to run the scripts | The scripts are Python, not part of your app's own stack | Any machine — doesn't have to be your app's server |

### A3. Application-level readiness (the part people skip)

| Checkpoint | Why it's required |
|---|---|
| ☐ You can describe what your app does in one sentence, business-language, not route names | This becomes your Service Offering description — "processes drone images into crop analytics," not "runs `/stitch/jobs`" |
| ☐ You know whether your app produces a standalone data asset (a report, dataset, export) | Determines whether you need a `gx:DataResource` entry or not |
| ☐ For each policy area that applies (retention, deletion, sharing, processing location, etc.) you can point to *how it's actually enforced* — a config value, a scheduled job, a DB table | This repo refuses to publish a policy claim with no evidence pointer — decide now, not while filling YAML |

**If any A3 box is unclear, do Phase 0 properly (below) before opening any
config file — it exists precisely to force these answers out of your head
and onto paper first.**

---

## Part B — Step-by-step usage

### Step 0 — Clone/copy the template

```bash
# unzip into your own new repo, or use it as a GitHub template
cd gaiax-compliance-template-v2
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Step 1 — Phase 0 assessment (no code, just documents)

Open `docs/PHASE_0_ASSESSMENT.md` and fill in, in order:

1. `docs/templates/application_inventory.md` — list what your app does, in
   plain business language.
2. `docs/templates/provider_inventory.md` — decide which legal entity is
   the Gaia-X Participant.
3. `docs/templates/service_inventory.md` — classify each application
   capability as an External Service Offering, Internal-only, or N/A. Most
   apps end up with **one** external offering.
4. `docs/templates/resource_inventory.md` — list any standalone data
   asset your service produces (or leave empty if none).
5. `docs/templates/policy_inventory.md` — for each real policy your app
   has, write the claim **and** how it's verifiable.

Don't skip to Step 2 until these five documents have real content, not
placeholders. This is genuinely the part that takes actual thought; every
step after this is mechanical transcription.

### Step 2 — Fill the mapping file

Open `gaiax/mapping.yaml`. For every capability you marked "External
Service Offering" in step 1.3, add a row mapping it to `gx:ServiceOffering`.
Same for your Participant (`gx:LegalParticipant`) and any data resources
(`gx:DataResource`). This file is what `validate_local.py` cross-checks
against your config — it's the paper trail proving your config isn't
arbitrary.

### Step 3 — Fill the config

Open `gaiax.config.yaml` and transcribe the decisions from Steps 1–2:
- `domain`, `participant.*` — from `provider_inventory.md`
- `service_offerings[]` — one entry per External Service Offering from
  `service_inventory.md`
- `data_resources[]` — from `resource_inventory.md` (leave `[]` if none)
- `policies.*` — **claim + evidence pairs** from `policy_inventory.md`;
  delete any policy block that doesn't genuinely apply to your app, don't
  leave it half-filled

Every `REPLACE_ME` must go. Nothing downstream will run until it does.

### Step 4 — Validate locally

```bash
python scripts/validate_local.py
```

This must print `Config OK` before you continue. Common first-run failures
and what they mean:
- **Unfilled placeholder** → go back and fill it, it'll tell you exactly which field.
- **Policy has claim but no evidence** → you can't just assert something is
  true, you need to say *how* — a DB table, a cron job, a config value.
- **data_resources produced_by doesn't match any service_offerings id** →
  typo, or you forgot to add the offering first.
- **mapping.yaml entry with unsupported gaiax_class** → typo in the class
  name, or you're trying to model an entity type this template doesn't
  generate yet.

### Step 5 — Generate keys and identity

```bash
python scripts/generate_keys.py
python scripts/generate_did.py
```

This writes `keys/private.pem` (**never commit this**, already gitignored)
and `.well-known/did.json`. Now **deploy the entire `.well-known/`
directory** to your domain, alongside your TLS certificate chain at
`.well-known/x509CertificateChain.pem`. Your identity is now resolvable at
`https://yourdomain.com/.well-known/did.json` — nothing else registers it,
Gaia-X just fetches this URL directly.

### Step 6 — Notarize your registration number

```bash
python scripts/request_lrn.py
```

Posts your VAT ID/LEI/EUID/EORI to the GXDCH Notarization API, which
checks it against the real business register and signs the result itself
— this is the one credential you don't sign. Requires outbound network
access to the GXDCH registry domain. Writes `.well-known/lrn.json` —
redeploy `.well-known/` again after this.

### Step 7 — Build and sign the rest

```bash
python scripts/build_credentials.py
```

Generates and signs: Participant, Terms & Conditions (text fetched live so
you're never signing a stale copy), one Service Offering per config entry,
one Data Resource per config entry, and `policy.json`. Redeploy
`.well-known/` again — every file in there needs to be live before the
next step.

### Step 8 — Submit for compliance

```bash
python scripts/submit_compliance.py
```

Builds a Verifiable Presentation referencing your public credential URLs
and submits it to the GXDCH Compliance Service. On success, writes
`.well-known/compliance-credential.json` — host that too, it's your actual
proof of compliance. On failure, the response usually tells you which
credential/field didn't validate; check `docs/FAQ.md` for common causes
(most often: files not actually reachable yet, or a schema field that's
moved since this template was written).

### Step 9 — Wire the metadata API into your app

Drop `api/fastapi_example.py` (or the Flask/Express equivalent) into your
existing backend. This serves everything you generated as live JSON
endpoints, and demonstrates merging the static `policy.json` claim with a
**live** database read — go implement `get_live_policy_facts()` (or the
equivalent) for real, using whatever your app already tracks, so your
published policy can never silently drift from what your system actually
does.

### Step 10 — Keep it honest going forward

- Any time your service description, data resources, or policies change,
  re-run Steps 3–8 (config → validate → rebuild → resubmit), don't
  hand-edit the generated `.well-known/` files directly.
- `docs/VERSIONING.md` covers what to do when `service_offerings[].version`
  bumps.
- `.github/workflows/continuous-compliance.yml` runs weekly and checks your
  hosted credentials are still live and well-formed — treat a failure there
  as urgent, it means something a Gaia-X consumer relies on just broke.

---

## Quick checklist to print/keep next to you

```
[ ] Legal entity + registration number identified
[ ] Domain + HTTPS + static hosting ready
[ ] Phase 0 docs filled (application/provider/service/resource/policy inventories)
[ ] gaiax/mapping.yaml filled
[ ] gaiax.config.yaml filled, validate_local.py passes
[ ] Keys + DID generated, .well-known/ deployed
[ ] LRN notarized
[ ] Credentials built + signed, .well-known/ redeployed
[ ] Submitted to Compliance Service, credential received
[ ] Metadata API mounted in the real app, live policy facts wired in
[ ] Continuous-compliance CI enabled
```

# Phase 0 — Repository & Business Assessment

**Do this before you open `gaiax.config.yaml`.**

v1 of this template started at the config file. That was a mistake: it let
you fill in a Service Offering before deciding *what your service offering
actually is*, which is a business decision, not a YAML-editing task. Gaia-X
compliance describes a **business capability offered through a Trust
Framework**, not a codebase. If you can't answer the questions below in
plain language, any JSON-LD you generate next will be guessing.

This phase produces five short documents. Templates for all five are in
`docs/templates/`. None of them require code — they're deliberately just
tables and short answers. Budget an hour, not a sprint.

## 1. `application_inventory.md` — what does the system actually do?

List the distinct things your application does, in business language, not
route names. "Uploads drone images", not `POST /captures`. This becomes the
raw material for everything else.

## 2. `provider_inventory.md` — who is actually offering this?

Which legal entity is the Gaia-X Participant? If more than one organization
touches this (a university lab, a spin-off company, a consortium), decide
*now* which one holds the identity — this can't be split later without
re-notarizing.

## 3. `service_inventory.md` — which capabilities become Gaia-X offerings?

Not every internal capability should be published. Classify each item from
your application inventory as:
- **External Service Offering** — something another Gaia-X participant could
  discover and consume.
- **Internal only** — supports the above but isn't independently offered.
- **Not applicable** — infrastructure, auth, admin tooling.

Most applications end up with **one** Service Offering describing the whole
external-facing capability (e.g. "drone image processing"), with the
internal steps (stitching, detection, counting) named as supporting
capabilities inside its description — not published as separate offerings.
Splitting into multiple offerings only makes sense if each piece is sold or
consumed independently by different customers.

## 4. `resource_inventory.md` — does the service produce or hold data assets?

Gaia-X has a distinct entity for this: `gx:DataResource`. If your service
produces something a consumer might want described separately from the
processing service itself (a dataset, a generated report, stored imagery),
list it here. This feeds `gaiax/data_resources/` in the config (new in v2 —
see `docs/INFORMATION_MODEL_MAPPING.md`).

## 5. `policy_inventory.md` — what governance actually exists today?

For each policy category (access, deletion, processing location, retention,
sharing, cross-border transfer, consent, audit), write down what your system
*actually does right now*, and — critically — **how someone could verify
it's true** (a config value, a cron job, a database table, an audit log).
That verification pointer is your compliance evidence, and it's what v2's
`policy.<name>.evidence` field expects. A policy claim with no evidence
pointer is a promise, not a compliance artifact — don't publish claims for
things you can't point at.

## Only after these five documents exist

Move on to `docs/INFORMATION_MODEL_MAPPING.md`, then `gaiax.config.yaml`.
The config file should now be a mechanical transcription of decisions you've
already made — not the place you make them.

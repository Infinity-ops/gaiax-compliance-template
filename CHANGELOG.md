# Changelog

## v2

Prompted by an external Gaia-X compliance review of v1. The review's full
text isn't reproduced here, but the substance of what changed and why:

**Adopted as-is:**
- Explicit business → Gaia-X Information Model mapping layer — the review's
  single biggest and most correct criticism, that v1 jumped from config
  straight to JSON-LD with the mapping only existing in the developer's
  head. Added `gaiax/mapping.yaml`, checked by `validate_local.py`.
- Evidence over claims — policies now require a `claim` + `evidence` pair;
  the build fails without both.
- `gx:DataResource` support — v1 only modeled Participant and Service
  Offering, missing that produced datasets/reports are their own Gaia-X
  entity with their own lifecycle.
- Versioning strategy and continuous compliance — v1 treated the Compliance
  Credential as a one-time output. Added `docs/VERSIONING.md` and a
  scheduled CI workflow that re-checks hosted credentials.
- Trust boundary / architecture diagrams — added to `docs/ARCHITECTURE.md`.
- Repository/business assessment before config — added as
  `docs/PHASE_0_ASSESSMENT.md` plus five fillable templates.

**Adopted with adjustment, not verbatim:**
- The review recommended splitting config into `participant.yaml`,
  `service.yaml`, `resource.yaml`, `policy.yaml` as separate files. Adopted
  the *separation of entities* (multiple offerings, separate data
  resources, named policies with their own evidence) but kept them as
  structured sections within one `gaiax.config.yaml` rather than four
  files — splitting files organizes the same information without adding
  correctness, and one file stays easier for a solo developer to review as
  a whole. Revisit if a project's config genuinely outgrows this.
- The review implied Phase 0 documents should be required gates before any
  technical work. They're strongly recommended and referenced throughout,
  but not mechanically enforced (e.g. `validate_local.py` doesn't check
  that `docs/templates/*.md` were edited) — a hard gate on prose documents
  is easy to game with placeholder text and would mostly create friction
  without a corresponding accuracy guarantee. The real enforcement is on
  `mapping.yaml` and `gaiax.config.yaml`, which are structured and checkable.

**Not adopted:**
- Nothing from the review was rejected outright; the "up to 10 policy
  categories" list was treated as a menu (add what applies) rather than a
  required checklist, per the review's own caveat that "not every
  application needs them all."

## v1

Initial release: config-driven Self-Description generation, DID:web
identity, GXDCH Notarization/Compliance Service scripting, FastAPI/Flask/
Express metadata endpoints.

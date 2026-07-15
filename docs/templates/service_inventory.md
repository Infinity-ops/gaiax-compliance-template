# Service Inventory

For every row in `application_inventory.md`, classify it:

| Capability | Classification | Why |
|---|---|---|
| e.g. Image ingestion | Internal only | Supports the offering, not independently consumed |
| e.g. Drone image processing (end-to-end) | **External Service Offering** | This is what a customer actually buys/consumes |
| e.g. Admin dashboard | Not applicable | Internal operations tooling |

Classification options:
- **External Service Offering** — becomes a `gx:ServiceOffering` in
  `gaiax.config.yaml`. Most projects have exactly one of these; having more
  than two or three is a sign you're describing implementation detail
  instead of a business capability — reconsider before proceeding.
- **Internal only** — mentioned in the Service Offering's description as
  part of how it works, never published as its own credential.
- **Not applicable** — leave out of Gaia-X artifacts entirely.

Once you have your list of External Service Offerings, each one gets its
own entry in `gaiax.config.yaml`'s `service_offerings:` list (v2 supports
more than one — see `docs/INFORMATION_MODEL_MAPPING.md`).

# Information Model Mapping

v1 of this template went straight from `gaiax.config.yaml` to JSON-LD. That
skipped a step: nothing recorded *why* a given config section corresponds
to a given Gaia-X ontology class. It worked, but only because the mapping
existed implicitly in the one developer's head who wrote the config.

v2 makes that mapping an explicit, checked artifact: `gaiax/mapping.yaml`.

## Why this matters in practice

Gaia-X is ontology-driven — every credential you publish asserts "this
JSON-LD document is an instance of `gx:ServiceOffering`" (or
`gx:LegalParticipant`, or `gx:DataResource`). The Compliance Service
validates your document against that class's required shape. If you (or a
future contributor) don't know *which* business concept is supposed to be
which class, you'll either misclassify something or duplicate effort
figuring it out again.

`gaiax/mapping.yaml` records, in one reviewable place:

```
business_object   → what this actually is, in plain language
gaiax_class       → which Gaia-X ontology class it's asserted to be
artifact          → which template file generates its JSON-LD
config_section    → where in gaiax.config.yaml its values come from
```

## How it's enforced

`scripts/validate_local.py` checks:
1. Every `config_section` referenced in `mapping.yaml` actually exists in
   `gaiax.config.yaml`.
2. Every `gaiax_class` is one of `supported_gaiax_classes` — i.e. this
   template actually knows how to generate that kind of artifact. If
   you need a Gaia-X class this template doesn't support yet (there are
   many — `gx:ServiceAccessPoint`, `gx:PhysicalResource`, etc.), that's a
   signal to add a template and generation step, not to silently skip
   the mapping.

## Extending it

Adding a new Gaia-X entity to your project (say, a `gx:DataResource` for a
second dataset) means:
1. Add a row to `docs/templates/resource_inventory.md`.
2. Add a row to `gaiax/mapping.yaml` pointing at it.
3. Add the corresponding entry to `gaiax.config.yaml`'s `data_resources:`
   list.
4. Re-run `scripts/build_credentials.py` — it iterates `data_resources:`
   and generates/signs one `gx:DataResource` credential per entry.

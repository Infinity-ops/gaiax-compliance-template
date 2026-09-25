#!/usr/bin/env python3
"""
Run this before anything else, and in CI on every PR. Fails loudly on:
  - unfilled REPLACE_ME placeholders in gaiax.config.yaml or mapping.yaml
  - policies with no evidence pointer (a claim nobody can verify)
  - data_resources referencing a service_offerings id that doesn't exist
  - mapping.yaml entries pointing at a Gaia-X class this template can't
    generate, or a config_section that doesn't exist

EXCEPTION: if the config is still in its pristine, un-started state (the
`domain` field is still exactly the shipped placeholder), this exits 0 with
a friendly notice instead of failing. Without this, the template repo's own
`main` branch — which always ships with an unfilled example config, by
design — would show a permanent red CI badge, and any fresh fork would see
a scary failure on day one before anyone has touched anything. The moment
`domain` is changed to a real value, full strict validation applies again —
that's the actual point where an incomplete config should start failing.

Usage: python scripts/validate_local.py
Exit code 0 = clean (or pristine/untouched), 1 = problems found.
"""
import sys
from _config import load_config, load_mapping, find_unfilled_placeholders

ERRORS = []


def error(msg):
    ERRORS.append(msg)


def check_placeholders(cfg, mapping):
    unfilled = find_unfilled_placeholders(cfg) + find_unfilled_placeholders(mapping)
    if unfilled:
        error("Unfilled REPLACE_ME placeholders:\n  " + "\n  ".join(f"- {p}" for p in unfilled))


def check_policy_evidence(cfg):
    for name, policy in (cfg.get("policies") or {}).items():
        claim = (policy or {}).get("claim")
        evidence = (policy or {}).get("evidence")
        if not claim:
            error(f"Policy '{name}' has no claim.")
        if not evidence:
            error(
                f"Policy '{name}' has a claim but no evidence pointer. "
                f"A claim nobody can verify isn't compliance evidence — "
                f"either fill in `evidence`, or delete this policy if it "
                f"doesn't apply. See docs/templates/policy_inventory.md."
            )


def check_data_resource_references(cfg):
    offering_ids = {o["id"] for o in cfg.get("service_offerings", [])}
    for res in cfg.get("data_resources") or []:
        produced_by = res.get("produced_by")
        if produced_by not in offering_ids:
            error(
                f"data_resources entry '{res.get('id')}' has produced_by="
                f"'{produced_by}', which doesn't match any service_offerings[].id "
                f"({sorted(offering_ids)})."
            )


def check_mapping_consistency(cfg, mapping):
    supported = set(mapping.get("supported_gaiax_classes", []))
    for m in mapping.get("mappings", []):
        gclass = m.get("gaiax_class")
        if gclass not in supported:
            error(
                f"mapping.yaml entry '{m.get('business_object')}' claims "
                f"gaiax_class '{gclass}', which isn't in supported_gaiax_classes. "
                f"Either fix a typo, or this template doesn't generate that "
                f"entity type yet — add a template + generation step first."
            )
        section = m.get("config_section", "")
        if section and section != "n/a" and "n/a" not in section:
            top = section.split("[")[0].split(".")[0]
            if top not in cfg:
                error(
                    f"mapping.yaml entry '{m.get('business_object')}' references "
                    f"config_section '{section}', but gaiax.config.yaml has no "
                    f"top-level '{top}' key."
                )


PRISTINE_DOMAIN = "REPLACE_ME.example.com"


def is_pristine_template(cfg):
    """True only for the exact, untouched shipped example config."""
    return cfg.get("domain") == PRISTINE_DOMAIN


def main():
    cfg = load_config()

    if is_pristine_template(cfg):
        print(
            "This is the unmodified template config — nothing to validate "
            "yet.\n\nStart with docs/PHASE_0_ASSESSMENT.md, then fill in "
            "gaiax/mapping.yaml and gaiax.config.yaml. Once you set a real "
            "`domain`, this check validates for real."
        )
        sys.exit(0)

    mapping = load_mapping()

    check_placeholders(cfg, mapping)
    check_policy_evidence(cfg)
    check_data_resource_references(cfg)
    check_mapping_consistency(cfg, mapping)

    if cfg["environment"] == "production":
        if cfg["participant"]["registration_type"] not in ("vatID", "leiCode", "EUID", "EORI"):
            error("environment is 'production' but registration_type is invalid.")
        print("WARNING: environment is 'production'. This will notarize a real "
              "registration number and submit real credentials to the live "
              "GXDCH. Make sure that's intended.\n")

    if ERRORS:
        print(f"{len(ERRORS)} problem(s) found:\n")
        for e in ERRORS:
            print(f"- {e}\n")
        sys.exit(1)

    print("Config OK — no placeholders, all policies have evidence, "
          "all references consistent.")


if __name__ == "__main__":
    main()
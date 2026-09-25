#!/usr/bin/env python3
"""
Renders and self-signs every credential described by gaiax.config.yaml:
  - Legal Participant           (1x)
  - Terms & Conditions          (1x, text fetched live from GXDCH registry)
  - Service Offering            (1x per entry in service_offerings[])
  - Data Resource               (1x per entry in data_resources[])
  - policy.json                 (1x, built directly from the policies map —
                                  not template-rendered, since its keys are
                                  variable; see docs/INFORMATION_MODEL_MAPPING.md)

Requires: scripts/generate_keys.py, scripts/generate_did.py, and
scripts/request_lrn.py already run.

Usage: python scripts/build_credentials.py
"""
import hashlib
import json
import os
import sys

import requests
from _config import load_config, gxdch_urls, render_template, find_unfilled_placeholders
from sign_credential import sign

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "gaiax", "templates")
WELL_KNOWN_DIR = os.path.join(os.path.dirname(__file__), "..", ".well-known")


def load_template(name):
    with open(os.path.join(TEMPLATE_DIR, name)) as f:
        return f.read()


def fetch_terms_and_conditions(cfg):
    url = f"{gxdch_urls(cfg)['registry']}/termsAndConditions"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text.strip()


def build_policy_json(cfg):
    """policy.json isn't template-rendered — its keys are whatever the user
    defined in policies:, so it's built directly from config. Every entry
    is required to have both `claim` and `evidence` (validate_local.py
    enforces this before this script is allowed to run)."""
    return {name: dict(policy) for name, policy in (cfg.get("policies") or {}).items()}


def main():
    cfg = load_config()
    if find_unfilled_placeholders(cfg):
        print("Config still has REPLACE_ME placeholders. Run "
              "scripts/validate_local.py for details, fix them, then retry.")
        sys.exit(1)

    priv_path = cfg["keys"]["private_key_path"]
    if not os.path.exists(priv_path):
        print(f"{priv_path} not found — run scripts/generate_keys.py first.")
        sys.exit(1)
    with open(priv_path, "rb") as f:
        private_key_pem = f.read()

    verification_method = f"did:web:{cfg['domain']}#JWK2020-RSA"
    issuer = f"did:web:{cfg['domain']}"
    os.makedirs(WELL_KNOWN_DIR, exist_ok=True)

    # 1. Terms & Conditions
    tnc_text = fetch_terms_and_conditions(cfg)
    tnc_hash = hashlib.sha256(tnc_text.encode("utf-8")).hexdigest()
    tnc_raw = render_template(load_template("terms-and-conditions.jsonld"), cfg)
    tnc = json.loads(tnc_raw)
    tnc["gx:termsAndConditions"] = tnc_text
    tnc["gx:hash"] = tnc_hash
    _write("tnc.json", sign(tnc, private_key_pem, verification_method, issuer))

    # 2. Legal Participant (references the LRN credential fetched separately
    #    via request_lrn.py — must already exist at .well-known/lrn.json)
    if not os.path.exists(os.path.join(WELL_KNOWN_DIR, "lrn.json")):
        print("Missing .well-known/lrn.json — run scripts/request_lrn.py first.")
        sys.exit(1)
    participant_raw = render_template(load_template("legal-participant.jsonld"), cfg)
    _write("participant.json", sign(json.loads(participant_raw), private_key_pem, verification_method, issuer))

    # 3. Policy document — built directly from config, not from a template
    _write("policy.json", build_policy_json(cfg))

    # 4. One Service Offering per entry in service_offerings[]
    offering_template = load_template("service-offering.jsonld")
    for offering in cfg.get("service_offerings", []):
        extra = {
            "offering_id": offering["id"],
            "offering_name": offering["name"],
            "offering_description": offering["description"],
            "offering_data_account_export.request_type": offering["data_account_export"]["request_type"],
            "offering_data_account_export.access_type": offering["data_account_export"]["access_type"],
            "offering_data_account_export.format": offering["data_account_export"]["format"],
            "offering_produces_resources": offering.get("produces_resources", []),
        }
        rendered = json.loads(render_template(offering_template, cfg, extra))
        signed = sign(rendered, private_key_pem, verification_method, issuer)
        _write(f"service-offering-{offering['id']}.json", signed)

    # 5. One Data Resource per entry in data_resources[]
    if cfg.get("data_resources"):
        resource_template = load_template("data-resource.jsonld")
        for resource in cfg["data_resources"]:
            extra = {
                "resource_id": resource["id"],
                "resource_name": resource["name"],
                "resource_description": resource["description"],
                "resource_format": resource["format"],
                "produced_by": resource["produced_by"],
                "resource_owner": resource["owner"],
                "resource_retention_claim": resource["retention_claim"],
                "resource_retention_evidence": resource["retention_evidence"],
                "resource_export_mechanism": resource["export_mechanism"],
            }
            rendered = json.loads(render_template(resource_template, cfg, extra))
            signed = sign(rendered, private_key_pem, verification_method, issuer)
            _write(f"data-resource-{resource['id']}.json", signed)

    print("\nAll credentials built and signed. Host the entire .well-known/ "
          "directory at your domain root, then run scripts/submit_compliance.py")


def _write(filename, obj):
    path = os.path.join(WELL_KNOWN_DIR, filename)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
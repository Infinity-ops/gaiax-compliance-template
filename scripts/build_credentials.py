#!/usr/bin/env python3
"""
Renders the Legal Participant, Terms & Conditions, and Service Offering
templates from gaiax.config.yaml, then self-signs each with your private
key. Requires: scripts/generate_keys.py, scripts/generate_did.py, and
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
    os.makedirs(WELL_KNOWN_DIR, exist_ok=True)

    # 1. Terms & Conditions
    tnc_text = fetch_terms_and_conditions(cfg)
    tnc_hash = hashlib.sha256(tnc_text.encode("utf-8")).hexdigest()
    tnc_raw = render_template(load_template("terms-and-conditions.jsonld"), cfg)
    tnc = json.loads(tnc_raw)
    tnc["gx:termsAndConditions"] = tnc_text
    tnc["gx:hash"] = tnc_hash
    tnc_signed = sign(tnc, private_key_pem, verification_method)
    _write("tnc.json", tnc_signed)

    # 2. Legal Participant (references the LRN credential fetched separately
    #    via request_lrn.py — must already exist at .well-known/lrn.json)
    if not os.path.exists(os.path.join(WELL_KNOWN_DIR, "lrn.json")):
        print("Missing .well-known/lrn.json — run scripts/request_lrn.py first.")
        sys.exit(1)
    participant_raw = render_template(load_template("legal-participant.jsonld"), cfg)
    participant = json.loads(participant_raw)
    participant_signed = sign(participant, private_key_pem, verification_method)
    _write("participant.json", participant_signed)

    # 3. Policy document (plain JSON, referenced by the Service Offering —
    #    not itself a signed credential in this minimal template)
    policy_raw = render_template(load_template("policy.json"), cfg)
    _write("policy.json", json.loads(policy_raw))

    # 4. Service Offering
    offering_raw = render_template(load_template("service-offering.jsonld"), cfg)
    offering = json.loads(offering_raw)
    offering_signed = sign(offering, private_key_pem, verification_method)
    _write("service-offering.json", offering_signed)

    print("\nAll credentials built and signed. Host the entire .well-known/ "
          "directory at your domain root, then run scripts/submit_compliance.py")


def _write(filename, obj):
    path = os.path.join(WELL_KNOWN_DIR, filename)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()

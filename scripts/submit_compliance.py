#!/usr/bin/env python3
"""
Bundles all hosted credentials into a Verifiable Presentation and submits
it to the GXDCH Compliance Service. On success, prints (and saves) the
resulting Gaia-X Compliance Credential.

IMPORTANT: this references credentials by their PUBLIC URLs
(https://{domain}/.well-known/...), not local disk — the Compliance
Service verifies documents the same way any other Gaia-X consumer would.
Deploy .well-known/ to your domain before running this.

Usage: python scripts/submit_compliance.py
"""
import glob
import json
import os
import sys

import requests
from _config import load_config, gxdch_urls, find_unfilled_placeholders

WELL_KNOWN_DIR = os.path.join(os.path.dirname(__file__), "..", ".well-known")


def discover_credential_files():
    """Every service-offering-*.json and data-resource-*.json actually
    generated, plus the fixed participant/tnc/lrn trio. Discovered from
    disk rather than hardcoded, so this stays correct regardless of how
    many offerings/resources are configured."""
    fixed = ["participant.json", "tnc.json", "lrn.json"]
    pattern_files = sorted(
        os.path.basename(p) for p in
        glob.glob(os.path.join(WELL_KNOWN_DIR, "service-offering-*.json"))
        + glob.glob(os.path.join(WELL_KNOWN_DIR, "data-resource-*.json"))
    )
    return fixed + pattern_files


def main():
    cfg = load_config()
    if find_unfilled_placeholders(cfg):
        print("Config still has REPLACE_ME placeholders. Fix them first.")
        sys.exit(1)

    domain = cfg["domain"]
    base = f"https://{domain}/.well-known"

    files = discover_credential_files()
    missing = [f for f in files if not os.path.exists(os.path.join(WELL_KNOWN_DIR, f))]
    if missing:
        print(f"Missing generated files: {missing}. Run scripts/build_credentials.py "
              f"(and scripts/request_lrn.py for lrn.json) first.")
        sys.exit(1)

    verifiable_presentation = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "type": ["VerifiablePresentation"],
        "verifiableCredential": [f"{base}/{f}" for f in files],
    }

    compliance_url = f"{gxdch_urls(cfg)['compliance']}/credential-offers"
    print(f"POST {compliance_url}")
    print(json.dumps(verifiable_presentation, indent=2))
    print(f"\nSubmitting... (the Compliance Service will fetch and verify each "
          f"credential URL above over HTTPS — make sure {base}/ is live)")

    resp = requests.post(compliance_url, json=verifiable_presentation, timeout=60)

    if resp.status_code >= 400:
        print(f"\nCompliance check FAILED ({resp.status_code}):")
        print(resp.text)
        print("\nCommon causes: credentials not yet publicly reachable at the "
              "URLs above, a template field that doesn't match the current "
              "GXDCH shape/schema, or a signature mismatch (re-run "
              "build_credentials.py after any config change).")
        sys.exit(1)

    result = resp.json()
    out_path = os.path.join(WELL_KNOWN_DIR, "compliance-credential.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nCompliance credential received. Wrote {out_path}")
    print("Host this file too — it's your proof of Gaia-X compliance.")


if __name__ == "__main__":
    main()

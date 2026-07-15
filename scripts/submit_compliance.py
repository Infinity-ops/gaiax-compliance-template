#!/usr/bin/env python3
"""
Bundles your hosted credentials into a Verifiable Presentation and submits
it to the GXDCH Compliance Service. On success, prints (and saves) the
resulting Gaia-X Compliance Credential — your proof of being a Gaia-X
Conformant Participant / Service Offering.

IMPORTANT: this fetches your credentials back from their PUBLIC URLs
(https://{domain}/.well-known/...), not from local disk — the whole point
is that the Compliance Service verifies documents the same way any other
Gaia-X consumer would. Make sure you've actually deployed .well-known/ to
your domain before running this.

Usage: python scripts/submit_compliance.py
"""
import json
import os
import sys

import requests
from _config import load_config, gxdch_urls, find_unfilled_placeholders

WELL_KNOWN_DIR = os.path.join(os.path.dirname(__file__), "..", ".well-known")


def main():
    cfg = load_config()
    if find_unfilled_placeholders(cfg):
        print("Config still has REPLACE_ME placeholders. Fix them first.")
        sys.exit(1)

    domain = cfg["domain"]
    base = f"https://{domain}/.well-known"

    verifiable_presentation = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "type": ["VerifiablePresentation"],
        "verifiableCredential": [
            f"{base}/participant.json",
            f"{base}/tnc.json",
            f"{base}/lrn.json",
            f"{base}/service-offering.json",
        ],
    }

    compliance_url = f"{gxdch_urls(cfg)['compliance']}/credential-offers"
    print(f"POST {compliance_url}")
    print(json.dumps(verifiable_presentation, indent=2))
    print("\nSubmitting... (the Compliance Service will fetch and verify each "
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
    print("Host this file too — it's your proof of Gaia-X compliance, and "
          "what api/fastapi_example.py serves at /gaia-x/compliance-credential.")


if __name__ == "__main__":
    main()

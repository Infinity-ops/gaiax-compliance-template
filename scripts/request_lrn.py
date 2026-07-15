#!/usr/bin/env python3
"""
Requests your Legal Registration Number (LRN) credential from the GXDCH
Notarization API. This is the one credential in the whole flow that you do
NOT sign yourself — the GXDCH verifies your VAT/EUID/LEI number against the
real registry and signs the credential on your behalf.

Usage: python scripts/request_lrn.py
"""
import json
import os
import sys

import requests
from _config import load_config, gxdch_urls, find_unfilled_placeholders

REG_TYPE_FIELD = {
    "vatID": "gx:vatID",
    "leiCode": "gx:leiCode",
    "EUID": "gx:EUID",
    "EORI": "gx:EORI",
}


def main():
    cfg = load_config()
    if find_unfilled_placeholders(cfg):
        print("Config still has REPLACE_ME placeholders. Run "
              "scripts/validate_local.py for details, fix them, then retry.")
        sys.exit(1)

    domain = cfg["domain"]
    reg_type = cfg["participant"]["registration_type"]
    reg_number = cfg["participant"]["registration_number"]
    field = REG_TYPE_FIELD[reg_type]

    lrn_id_url = f"https://{domain}/.well-known/lrn.json"
    vcid = f"{lrn_id_url}#subject"

    payload = {
        "@context": [
            f"{gxdch_urls(cfg)['registry']}/trusted-shape-registry/v1/shapes/jsonld/participant"
        ],
        "type": "gx:legalRegistrationNumber",
        "id": lrn_id_url,
        field: reg_number,
    }

    notary_url = f"{gxdch_urls(cfg)['notary']}/registrationNumberVC?vcid={vcid}"
    print(f"POST {notary_url}")
    print(json.dumps(payload, indent=2))

    resp = requests.post(notary_url, json=payload, timeout=30)

    if resp.status_code >= 400:
        print(f"\nNotarization FAILED ({resp.status_code}):")
        print(resp.text)
        sys.exit(1)

    out_dir = os.path.join(os.path.dirname(__file__), "..", ".well-known")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "lrn.json")
    with open(out_path, "w") as f:
        f.write(resp.text)

    print(f"\nNotarization succeeded. Wrote {out_path}")
    print(f"Host this at: {lrn_id_url}")


if __name__ == "__main__":
    main()

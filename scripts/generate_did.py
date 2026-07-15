#!/usr/bin/env python3
"""
Builds .well-known/did.json for did:web:<your-domain>. Host this file
(along with your TLS cert chain at .well-known/x509CertificateChain.pem)
at your real domain over HTTPS — Gaia-X resolves your identity by fetching
this URL, there's no separate registration step for the DID itself.

Usage: python scripts/generate_did.py
"""
import base64
import json
import os
from cryptography.hazmat.primitives import serialization
from _config import load_config


def main():
    cfg = load_config()
    domain = cfg["domain"]
    pub_path = cfg["keys"]["public_key_path"]

    if not os.path.exists(pub_path):
        print(f"{pub_path} not found — run scripts/generate_keys.py first.")
        return

    with open(pub_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    numbers = public_key.public_numbers()
    n = base64.urlsafe_b64encode(
        numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")
    ).rstrip(b"=").decode()
    e = base64.urlsafe_b64encode(
        numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")
    ).rstrip(b"=").decode()

    did_document = {
        "@context": [
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/suites/jws-2020/v1",
        ],
        "id": f"did:web:{domain}",
        "verificationMethod": [
            {
                "id": f"did:web:{domain}#JWK2020-RSA",
                "type": "JsonWebKey2020",
                "controller": f"did:web:{domain}",
                "publicKeyJwk": {
                    "kty": "RSA",
                    "n": n,
                    "e": e,
                    "alg": "PS256",
                },
            }
        ],
        "assertionMethod": [f"did:web:{domain}#JWK2020-RSA"],
    }

    out_dir = os.path.join(os.path.dirname(__file__), "..", ".well-known")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "did.json")
    with open(out_path, "w") as f:
        json.dump(did_document, f, indent=2)

    print(f"Wrote {out_path}")
    print(f"\nHost this at: https://{domain}/.well-known/did.json")
    print(f"Also host your TLS cert chain at: https://{domain}/.well-known/x509CertificateChain.pem")
    print(f"\nYour identity will resolve as: did:web:{domain}")


if __name__ == "__main__":
    main()

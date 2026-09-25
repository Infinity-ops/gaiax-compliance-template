#!/usr/bin/env python3
"""
Signs a JSON-LD credential with your private key, producing a Gaia-X-style
"proof" block (JsonWebSignature2020 over the URDNA2015-normalized document).
Used by build_credentials.py — you generally won't call this file directly.
"""
import json
from hashlib import sha256

from jwcrypto import jwk, jws
from jwcrypto.common import json_encode
from pyld import jsonld


def sign(credential: dict, private_key_pem: bytes, verification_method: str, issuer: str) -> dict:
    """Returns a copy of `credential` with `issuer` and a `proof` block
    attached.

    `issuer` MUST be set before normalization/signing — it's part of what
    gets signed, not metadata added afterward. Per the W3C Verifiable
    Credential Data Model, `issuer` is a mandatory top-level field, and the
    GXDCH Compliance Service resolves it to check that `verificationMethod`
    in the proof actually belongs to that issuer. A credential signed
    without `issuer` set is one the Compliance Service cannot attribute to
    anyone — this is a common cause of an opaque "proof not found" error
    from the Compliance Service, since it has nothing to resolve the proof
    against.
    """
    credential = dict(credential)
    credential["issuer"] = issuer

    key = jwk.JWK.from_pem(private_key_pem)

    normalized = jsonld.normalize(
        credential, {"algorithm": "URDNA2015", "format": "application/n-quads"}
    )
    digest = sha256(normalized.encode("utf-8")).hexdigest()

    token = jws.JWS(digest)
    protected_header = json_encode({"alg": "PS256", "b64": False, "crit": ["b64"]})
    token.add_signature(key, None, protected_header)
    serialized = token.serialize(compact=True)
    header, _, signature = serialized.split(".")

    signed = dict(credential)
    signed["proof"] = {
        "type": "JsonWebSignature2020",
        "created": _now_iso(),
        "proofPurpose": "assertionMethod",
        "verificationMethod": verification_method,
        "jws": f"{header}..{signature}",
    }
    return signed


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    print("This module is a library used by build_credentials.py — "
          "run that script instead.")
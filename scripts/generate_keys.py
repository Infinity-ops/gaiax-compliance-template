#!/usr/bin/env python3
"""
Generate the RSA key pair used to sign your self-issued Gaia-X credentials
(Participant, Terms & Conditions, Service Offering). The LRN credential is
signed by the GXDCH instead — see request_lrn.py.

Usage: python scripts/generate_keys.py
"""
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from _config import load_config


def main():
    cfg = load_config()
    priv_path = cfg["keys"]["private_key_path"]
    pub_path = cfg["keys"]["public_key_path"]
    os.makedirs(os.path.dirname(priv_path) or ".", exist_ok=True)

    if os.path.exists(priv_path):
        print(f"{priv_path} already exists — refusing to overwrite. "
              f"Delete it manually first if you really want a new key.")
        return

    key = rsa.generate_private_key(public_exponent=65537, key_size=cfg["keys"]["key_size"])

    with open(priv_path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    os.chmod(priv_path, 0o600)

    with open(pub_path, "wb") as f:
        f.write(key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))

    print(f"Wrote {priv_path} (chmod 600 — keep it secret, never commit it)")
    print(f"Wrote {pub_path}")
    print("\nMake sure keys/private.pem is in .gitignore.")


if __name__ == "__main__":
    main()

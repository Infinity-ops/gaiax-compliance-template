#!/usr/bin/env python3
"""
Run this before anything else, and in CI on every PR. Fails loudly if
gaiax.config.yaml still has REPLACE_ME placeholders, so nobody accidentally
notarizes or publishes fake identity/policy data.

Usage: python scripts/validate_local.py
Exit code 0 = clean, 1 = placeholders remain.
"""
import sys
from _config import load_config, find_unfilled_placeholders


def main():
    cfg = load_config()
    unfilled = find_unfilled_placeholders(cfg)

    if unfilled:
        print("gaiax.config.yaml has unfilled REPLACE_ME placeholders:\n")
        for path in unfilled:
            print(f"  - {path}")
        print("\nFill these in before generating or submitting any credentials.")
        sys.exit(1)

    if cfg["environment"] == "production" and cfg["participant"]["registration_type"] not in (
        "vatID", "leiCode", "EUID", "EORI",
    ):
        print("environment is 'production' but registration_type is invalid.")
        sys.exit(1)

    if cfg["environment"] == "production":
        print("WARNING: environment is set to 'production'. This will notarize a "
              "real registration number and submit real credentials to the live "
              "GXDCH. Make sure that's intended.")

    print("Config OK — no placeholders remaining.")


if __name__ == "__main__":
    main()

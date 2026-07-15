"""
Reference Gaia-X metadata router for FastAPI.

Mount this in your existing app:

    from api.fastapi_example import router as gaiax_router
    app.include_router(gaiax_router, prefix="/gaia-x", tags=["gaia-x"])

It serves the static credentials you generated in .well-known/, plus one
example of merging a static policy claim with a LIVE value from your own
database — copy this pattern for any policy field your app already tracks
dynamically (retention rules, active data-sharing agreements, etc.), rather
than letting a static file drift out of sync with what your system enforces.
"""
import json
import os

from fastapi import APIRouter, HTTPException

router = APIRouter()

WELL_KNOWN_DIR = os.path.join(os.path.dirname(__file__), "..", ".well-known")


def _load(filename: str) -> dict:
    path = os.path.join(WELL_KNOWN_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(
            status_code=503,
            detail=f"{filename} not generated yet — run scripts/build_credentials.py",
        )
    with open(path) as f:
        return json.load(f)


@router.get("/participant")
def participant():
    return _load("participant.json")


@router.get("/service-offering")
def service_offering():
    return _load("service-offering.json")


@router.get("/terms-and-conditions")
def terms_and_conditions():
    return _load("tnc.json")


@router.get("/policy")
def policy():
    """
    EXAMPLE of keeping a published policy honest: start from the static
    claim, then overlay live facts from your own system. Replace the
    `get_live_retention_rules()` stub below with a real query against
    whatever table/service in your app actually enforces retention,
    sharing, or deletion.
    """
    static_policy = _load("policy.json")
    static_policy["liveRetentionRules"] = get_live_retention_rules()
    return static_policy


def get_live_retention_rules():
    """
    Stub — replace with a real query. Example shape shown here matches
    a typical "cleanup policy" table pattern:

        return [
            {"name": p.name, "enabled": p.enabled, "max_age_days": p.max_age_days}
            for p in db.query(CleanupPolicy).all()
        ]
    """
    return []


@router.get("/compliance-credential")
def compliance_credential():
    return _load("compliance-credential.json")

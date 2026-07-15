"""
Reference Gaia-X metadata router for FastAPI.

Mount this in your existing app:

    from api.fastapi_example import router as gaiax_router
    app.include_router(gaiax_router, prefix="/gaia-x", tags=["gaia-x"])

Serves whatever scripts/build_credentials.py generated into .well-known/ —
one or more service offerings and data resources, discovered by id rather
than hardcoded, plus the fixed participant/terms/policy/compliance
documents. Also demonstrates merging a static policy claim with a LIVE
value read from your own database (copy this pattern for any policy field
your app already tracks dynamically instead of letting a static file drift
out of sync with what your system actually enforces).
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


@router.get("/service-offerings")
def list_service_offerings():
    """Every generated offering, by id — so a consumer can discover what's
    published without knowing filenames in advance."""
    prefix, suffix = "service-offering-", ".json"
    ids = [
        f[len(prefix):-len(suffix)]
        for f in os.listdir(WELL_KNOWN_DIR)
        if f.startswith(prefix) and f.endswith(suffix)
    ]
    return {"offerings": ids}


@router.get("/service-offerings/{offering_id}")
def service_offering(offering_id: str):
    return _load(f"service-offering-{offering_id}.json")


@router.get("/data-resources")
def list_data_resources():
    prefix, suffix = "data-resource-", ".json"
    ids = [
        f[len(prefix):-len(suffix)]
        for f in os.listdir(WELL_KNOWN_DIR)
        if f.startswith(prefix) and f.endswith(suffix)
    ]
    return {"resources": ids}


@router.get("/data-resources/{resource_id}")
def data_resource(resource_id: str):
    return _load(f"data-resource-{resource_id}.json")


@router.get("/terms-and-conditions")
def terms_and_conditions():
    return _load("tnc.json")


@router.get("/policy")
def policy():
    """
    EXAMPLE of keeping a published policy honest: start from the static
    claim+evidence pairs, then overlay live facts from your own system
    wherever you can. Replace get_live_policy_facts() below with a real
    query against whatever in your app enforces retention, sharing, or
    deletion — a static claim should describe the mechanism, a live
    endpoint should confirm it's still true.
    """
    static_policy = _load("policy.json")
    live = get_live_policy_facts()
    if live:
        static_policy["liveFacts"] = live
    return static_policy


def get_live_policy_facts():
    """
    Stub — replace with a real query. Example shape matches a typical
    "cleanup policy" table pattern:

        return {
            "retention": [
                {"name": p.name, "enabled": p.enabled, "max_age_days": p.max_age_days}
                for p in db.query(CleanupPolicy).all()
            ]
        }
    """
    return {}


@router.get("/compliance-credential")
def compliance_credential():
    return _load("compliance-credential.json")

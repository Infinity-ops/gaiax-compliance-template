"""
Reference Gaia-X metadata blueprint for Flask.

Mount this in your existing app:

    from api.flask_example import gaiax_bp
    app.register_blueprint(gaiax_bp, url_prefix="/gaia-x")
"""
import json
import os

from flask import Blueprint, jsonify, abort

gaiax_bp = Blueprint("gaiax", __name__)

WELL_KNOWN_DIR = os.path.join(os.path.dirname(__file__), "..", ".well-known")


def _load(filename: str) -> dict:
    path = os.path.join(WELL_KNOWN_DIR, filename)
    if not os.path.exists(path):
        abort(503, description=f"{filename} not generated yet — run scripts/build_credentials.py")
    with open(path) as f:
        return json.load(f)


@gaiax_bp.route("/participant")
def participant():
    return jsonify(_load("participant.json"))


@gaiax_bp.route("/service-offering")
def service_offering():
    return jsonify(_load("service-offering.json"))


@gaiax_bp.route("/terms-and-conditions")
def terms_and_conditions():
    return jsonify(_load("tnc.json"))


@gaiax_bp.route("/policy")
def policy():
    static_policy = _load("policy.json")
    # Replace with a real query — see fastapi_example.py for the pattern.
    static_policy["liveRetentionRules"] = []
    return jsonify(static_policy)


@gaiax_bp.route("/compliance-credential")
def compliance_credential():
    return jsonify(_load("compliance-credential.json"))

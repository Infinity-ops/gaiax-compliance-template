"""Shared helpers: load gaiax.config.yaml + gaiax/mapping.yaml, and fill
{dotted.path} placeholders in the JSON-LD templates. Not a script — imported
by the others.
"""
import os
import re
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "gaiax.config.yaml")
MAPPING_PATH = os.path.join(os.path.dirname(__file__), "..", "gaiax", "mapping.yaml")

PLACEHOLDER = re.compile(r"REPLACE_ME")


def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def load_mapping():
    with open(MAPPING_PATH) as f:
        return yaml.safe_load(f)


def gxdch_urls(cfg):
    return cfg["gxdch"][cfg["environment"]]


def _lookup(cfg, dotted_path):
    node = cfg
    for part in dotted_path.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            raise KeyError(f"Config is missing '{dotted_path}' (failed at '{part}')")
    return node


def render_template(template_text, cfg, extra=None):
    """Replace {domain}, {section.field}, and {extra_key} placeholders.

    `extra` is a flat dict checked BEFORE falling back to a dotted lookup
    in `cfg` — used for per-item values when rendering one instance out of
    a list (e.g. a single service_offerings[] entry or data_resources[]
    entry), where the value doesn't live at a fixed path in the global
    config.
    """
    extra = extra or {}

    def replace(match):
        path = match.group(1)
        if path in extra:
            resolved = extra[path]
        elif path == "domain":
            resolved = cfg["domain"]
        else:
            resolved = _lookup(cfg, path)
        if isinstance(resolved, (list, dict)):
            import json
            return json.dumps(resolved)
        return str(resolved)

    return re.sub(r"\{([a-zA-Z0-9_.]+)\}", replace, template_text)


def find_unfilled_placeholders(node, prefix=""):
    """Recursively find every REPLACE_ME left in a config-like structure."""
    hits = []
    if isinstance(node, dict):
        for k, v in node.items():
            hits += find_unfilled_placeholders(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            hits += find_unfilled_placeholders(v, f"{prefix}[{i}]")
    elif isinstance(node, str) and PLACEHOLDER.search(node):
        hits.append(prefix)
    return hits

"""Shared helpers: load gaiax.config.yaml and fill {dotted.path} placeholders
in the JSON-LD templates. Not a script — imported by the others."""
import os
import re
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "gaiax.config.yaml")

PLACEHOLDER = re.compile(r"REPLACE_ME")


def load_config():
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)
    return cfg


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


def render_template(template_text, cfg):
    """Replace {domain} and {section.field} placeholders with config values."""

    def replace(match):
        path = match.group(1)
        value = "domain" if path == "domain" else path
        resolved = cfg["domain"] if path == "domain" else _lookup(cfg, path)
        if isinstance(resolved, (list, dict)):
            import json
            return json.dumps(resolved)
        return str(resolved)

    return re.sub(r"\{([a-zA-Z0-9_.]+)\}", replace, template_text)


def find_unfilled_placeholders(cfg, prefix=""):
    """Recursively find every REPLACE_ME left in the config."""
    hits = []
    if isinstance(cfg, dict):
        for k, v in cfg.items():
            hits += find_unfilled_placeholders(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(cfg, list):
        for i, v in enumerate(cfg):
            hits += find_unfilled_placeholders(v, f"{prefix}[{i}]")
    elif isinstance(cfg, str) and PLACEHOLDER.search(cfg):
        hits.append(prefix)
    return hits

#!/usr/bin/env python3
"""Validate blueprint manifests in this source repo.

Checks every blueprints/<id>/blueprint.yml has the required fields, the id
matches the server's regex, and the referenced config file exists and parses.
Add your own checks below.
"""
import os
import re
import sys
import yaml

ID_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_\-]*(/[A-Za-z0-9_\-]+){0,2}$')
REQUIRED = {"manifest_version", "id", "name", "description", "version", "config"}


def main() -> int:
    fail = False
    for d in sorted(os.listdir("blueprints")):
        manifest = f"blueprints/{d}/blueprint.yml"
        if not os.path.isfile(manifest):
            print(f"::error::{manifest} missing")
            fail = True
            continue
        with open(manifest) as f:
            m = yaml.safe_load(f) or {}
        missing = REQUIRED - m.keys()
        if missing:
            print(f"::error::{manifest} missing fields: {sorted(missing)}")
            fail = True
        if "id" in m and not ID_RE.match(str(m["id"])):
            print(f"::error::{manifest} invalid id: {m['id']!r}")
            fail = True
        cfg = f"blueprints/{d}/{m.get('config', 'range-config.yml')}"
        if not os.path.isfile(cfg):
            print(f"::error::{cfg} missing")
            fail = True
            continue
        try:
            yaml.safe_load(open(cfg))
        except yaml.YAMLError as e:
            print(f"::error::{cfg} invalid YAML: {e}")
            fail = True
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())

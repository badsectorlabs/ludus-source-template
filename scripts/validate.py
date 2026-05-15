#!/usr/bin/env python3
"""Validate the manifests in this Ludus source.

A Ludus source can ship any combination of Packer templates, Ansible roles,
and blueprints. This script checks whatever is present:

  - source.yml       (optional file)   -- manifest_version required if present
  - blueprints/<id>/blueprint.yml      -- required fields when the dir exists
  - blueprints/<id>/<config>           -- referenced by blueprint.yml.config
  - blueprints/<id>/requirements.yml   -- schema check for roles/collections/
                                          subscription_roles when present
  - dependency closure                 -- every role referenced under `roles:`
                                          in range-config.yml must be declared
                                          (requirements.yml roles, parent
                                          collection for FQCN refs,
                                          subscription_roles) or bundled
                                          locally (blueprint roles/ or source-
                                          root roles/)

A source with only roles/ or templates/ is valid and exits clean. An empty
source is rejected.

Add your own checks below.
"""
import os
import re
import sys
import yaml

ID_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_\-]*(/[A-Za-z0-9_\-]+){0,2}$')
BLUEPRINT_REQUIRED = {"manifest_version", "id", "name", "description", "version", "config"}
SOURCE_REQUIRED = {"manifest_version"}


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f) or {}


def validate_source_yml(fail):
    if not os.path.isfile("source.yml"):
        return fail
    try:
        m = load_yaml("source.yml")
    except yaml.YAMLError as e:
        print(f"::error::source.yml invalid YAML: {e}")
        return True
    missing = SOURCE_REQUIRED - m.keys()
    if missing:
        print(f"::error::source.yml missing fields: {sorted(missing)}")
        fail = True
    return fail


def parse_requirements(path):
    """Return (roles_set, collections_set, subscription_roles_set, ok)."""
    if not os.path.isfile(path):
        return set(), set(), set(), True
    try:
        doc = load_yaml(path) or {}
    except yaml.YAMLError as e:
        print(f"::error::{path} invalid YAML: {e}")
        return set(), set(), set(), False

    roles = set()
    for r in (doc.get("roles") or []):
        if isinstance(r, dict) and r.get("name"):
            roles.add(str(r["name"]))
        elif isinstance(r, str):
            roles.add(r)
        else:
            print(f"::error::{path} roles entry must be a mapping with `name:` or a bare string: {r!r}")
            return set(), set(), set(), False

    collections = set()
    for c in (doc.get("collections") or []):
        if isinstance(c, dict) and c.get("name"):
            collections.add(str(c["name"]))
        elif isinstance(c, str):
            collections.add(c)
        else:
            print(f"::error::{path} collections entry must be a mapping with `name:` or a bare string: {c!r}")
            return set(), set(), set(), False

    sub_roles = set()
    for s in (doc.get("subscription_roles") or []):
        if isinstance(s, dict) and s.get("name"):
            sub_roles.add(str(s["name"]))
        elif isinstance(s, str):
            sub_roles.add(s)
        else:
            print(f"::error::{path} subscription_roles entry must be a mapping with `name:` or a bare string: {s!r}")
            return set(), set(), set(), False

    return roles, collections, sub_roles, True


def role_refs_in_range_config(path):
    """Walk every `roles:` list under a `ludus:` host and return the union."""
    try:
        doc = load_yaml(path) or {}
    except yaml.YAMLError:
        return set()
    refs = set()
    hosts = doc.get("ludus") or []
    if not isinstance(hosts, list):
        return refs
    for host in hosts:
        if not isinstance(host, dict):
            continue
        for r in (host.get("roles") or []):
            if isinstance(r, dict) and r.get("role"):
                refs.add(str(r["role"]))
            elif isinstance(r, str):
                refs.add(r)
    return refs


def bundled_role_names(blueprint_id):
    """Return roles bundled in blueprint or at source root."""
    names = set()
    for parent in (f"blueprints/{blueprint_id}/roles", "roles"):
        if os.path.isdir(parent):
            for d in os.listdir(parent):
                if os.path.isdir(os.path.join(parent, d)):
                    names.add(d)
    return names


def validate_blueprint(d, fail):
    manifest = f"blueprints/{d}/blueprint.yml"
    if not os.path.isfile(manifest):
        print(f"::error::{manifest} missing")
        return True
    try:
        m = load_yaml(manifest)
    except yaml.YAMLError as e:
        print(f"::error::{manifest} invalid YAML: {e}")
        return True
    missing = BLUEPRINT_REQUIRED - m.keys()
    if missing:
        print(f"::error::{manifest} missing fields: {sorted(missing)}")
        fail = True
    if "id" in m and not ID_RE.match(str(m["id"])):
        print(f"::error::{manifest} invalid id: {m['id']!r}")
        fail = True
    cfg = f"blueprints/{d}/{m.get('config', 'range-config.yml')}"
    if not os.path.isfile(cfg):
        print(f"::error::{cfg} missing")
        return True
    try:
        load_yaml(cfg)
    except yaml.YAMLError as e:
        print(f"::error::{cfg} invalid YAML: {e}")
        return True

    reqs_path = f"blueprints/{d}/requirements.yml"
    declared_roles, declared_collections, declared_sub, ok = parse_requirements(reqs_path)
    if not ok:
        return True

    bundled = bundled_role_names(d)

    for ref in role_refs_in_range_config(cfg):
        if ref in bundled or ref in declared_roles or ref in declared_sub:
            continue
        parts = ref.split(".")
        if len(parts) >= 3:
            parent = ".".join(parts[:2])
            if parent in declared_collections:
                continue
            print(
                f"::error::{cfg}: role {ref!r} is a FQCN reference but its parent "
                f"collection {parent!r} is not declared in {reqs_path} under "
                f"`collections:`"
            )
            fail = True
            continue
        print(
            f"::error::{cfg}: role {ref!r} is referenced but not declared in "
            f"{reqs_path} (`roles:` or `subscription_roles:`) and not bundled "
            f"locally under roles/"
        )
        fail = True

    return fail


def main() -> int:
    fail = False
    fail = validate_source_yml(fail)

    has_blueprints = os.path.isdir("blueprints") and any(
        os.path.isdir(f"blueprints/{d}") for d in os.listdir("blueprints")
    )
    has_roles = os.path.isdir("roles") and any(
        os.path.isdir(f"roles/{d}") for d in os.listdir("roles")
    )
    has_templates = os.path.isdir("templates") and any(
        os.path.isdir(f"templates/{d}") for d in os.listdir("templates")
    )

    if not (has_blueprints or has_roles or has_templates):
        print("::error::source ships nothing; populate at least one of blueprints/, roles/, or templates/")
        return 1

    if has_blueprints:
        for d in sorted(os.listdir("blueprints")):
            if os.path.isdir(f"blueprints/{d}"):
                fail = validate_blueprint(d, fail)

    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())

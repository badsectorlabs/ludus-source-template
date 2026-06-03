# Blueprints

Each `blueprints/<id>/` directory is one blueprint — a named, versioned range config plus its dependencies:

```
blueprints/example/
├── blueprint.yml       display metadata
├── range-config.yml    the range config
└── requirements.yml    galaxy roles, collections, subscription roles
```

Installed blueprints are per-source, addressed as `<sourceID>/<id>` (e.g. `ludus blueprint apply my-repo/example`). The example files here are annotated inline.

## Required fields

`blueprint.yml` requires:

- `manifest_version` — schema version, leave at `1`
- `id` — unique within the source; lowercase, dashes
- `name` — display name
- `description` — one-line summary
- `version` — your semver (see [Versioning](#versioning))
- `config` — path to the range config, relative to `blueprint.yml`

Optional: `tags`, `thumbnail`, `min_ludus_version`. License, homepage, and authors are inherited from the source's `source.yml`.

## Role and collection dependencies

`blueprints/<id>/requirements.yml` is the single manifest for everything a blueprint needs from outside the bundle. Every role referenced under `roles:` in `range-config.yml` must be declared here (or shipped locally under `roles/`); Ludus surfaces an undeclared-dependency warning at sync time otherwise.

Three sections, all optional:

```yaml
roles:
  - name: geerlingguy.docker
    version: 7.4.4                                  # pin a galaxy role
  - name: badsectorlabs.ludus_adcs                  # off-galaxy: name + src
    src: https://github.com/badsectorlabs/ludus_adcs
    version: v1.2.0

collections:
  - name: community.crypto                          # required when range-config
    version: 2.16.0                                 # references a FQCN role
                                                    # like community.crypto.openssl_certificate

subscription_roles:
  - ludus_ghosts_client                             # license-gated role; bare scalar
  - name: ludus_adcs                                # or structured shape
```

A few rules worth knowing:

- **Names must match** what `range-config.yml` references; otherwise Ludus installs one role and tries to run another.
- **Collections are required for FQCN role refs.** A 3-part reference like `namespace.collection.role` won't work unless `namespace.collection` is listed under `collections:`.
- **Subscription roles never travel in the bundle** — only their names. At apply time Ludus serves them from the license catalog. If the target instance has no valid license, or the catalog doesn't cover one of the names, the apply returns `403`. Version pinning isn't currently supported for subscription roles — whatever the catalog reports as current gets installed.
- **Local roles win over galaxy.** If a `roles/<name>/` directory exists in the bundle (per-blueprint or at source root), it satisfies the dependency without a galaxy lookup. See [`roles/`](../roles/README.md).

## Versioning

Two separate fields:

- `manifest_version` is the schema version of the manifest file. Ludus bumps it when the format changes incompatibly. Leave it at `1`.
- `version` is your semver for the blueprint. Bump it any time you change a blueprint and want users to see it as new. Push to your repo, then users run:

```bash
ludus source sync <repo>                # re-pull the source + refresh the catalog (read-only)
ludus blueprint info <repo>/example     # see the new version + dependency status
ludus blueprint install <repo>/example  # install any new role/collection deps it added
ludus blueprint apply <repo>/example    # write the updated config to your range
ludus range deploy                      # rebuild
```

`ludus blueprint apply` always writes whatever's currently in the source; there's no automatic upgrade prompt. The `version` field is for display and changelog purposes; pin to a git tag (`source update <repo> --ref v1.2.0`) to lock users to a specific release.

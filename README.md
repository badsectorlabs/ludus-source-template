# Ludus Source Template

A Ludus source is a versioned bundle of Packer templates, Ansible roles, and blueprints, served from a git repo, tarball, or local directory. `ludus source add` registers the contents in one step.

This repo is a starting point for publishing your own source. Use it as a template (or clone it and repoint `origin` at your new repo), edit the files, push, then run:

```bash
ludus source add https://github.com/<you>/<repo>
ludus blueprint apply <repo>/example   # if your source ships a blueprint
ludus range deploy
```

Any git host works (GitHub, GitLab, self-hosted). You can also pass `source add` a local tarball (`source add ./source.tar.gz`) or a local directory (`source add -d ./my-source`). Full reference: [Sources](https://docs.ludus.cloud/docs/using-ludus/sources).

## What you can ship

A source can carry any combination of three artifact types. All three are optional, but a source must ship at least one. Each has its own guide:

| Artifact         | Where it goes        | Visibility                                      | Guide                               |
|------------------|----------------------|-------------------------------------------------|-------------------------------------|
| Blueprints       | `blueprints/<id>/`   | Per-source, addressed as `<sourceID>/<id>`      | [blueprints/](blueprints/README.md) |
| Packer templates | `templates/<name>/`  | Per-user, keyed by the `*-template` name        | [templates/](templates/README.md)   |
| Ansible roles    | `ansible/roles/<name>/`       | User-scoped; `--global-roles` for instance-wide | [ansible/roles/](ansible/roles/README.md)             |
| Ansible collections | `ansible/collections/<dir>/` | User-scoped; `--global-roles` for instance-wide | [ansible/collections/](ansible/collections/README.md) |

A blueprints-only source, a roles-only source, and a templates-only source are all valid.

## Layout

```
LICENSE                              MIT placeholder; replace with your own
source.yml                           repo metadata (see below)

blueprints/                          blueprints + their dependencies — see blueprints/README.md
templates/                           Packer templates — see templates/README.md
ansible/roles/                       local Ansible roles — see ansible/roles/README.md
ansible/collections/                 local Ansible collections — see ansible/collections/README.md
```

The manifest schema is validated by Ludus when the source is registered or synced (`ludus source add`).

## Submodules

Any asset subdirectory — a blueprint, template, role (`ansible/roles/<name>/`) or
collection (`ansible/collections/<dir>/`) — can be a **git submodule**. When you
register or sync a git-backed source, Ludus clones it with `--recurse-submodules`,
so submodules are pulled (and refreshed on re-sync) automatically. This lets a
source aggregate content that lives in its own repository while keeping that repo
independent for issues and development.

Use **relative** submodule URLs (e.g. `../ludus_adcs.git`) in `.gitmodules` so the
source resolves submodules against whatever host it was cloned from.

## source.yml

Repo-level metadata at the source root, and the whole file is optional — when absent, Ludus derives the name from the URL and the homepage from the git remote. Only `manifest_version` is required when the file is present (leave it at `1`); `name`, `description`, `authors`, `homepage`, and `license` are optional. `authors`, `homepage`, and `license` apply to every blueprint in the source. The example is annotated inline.

## More

Full reference: [Sources](https://docs.ludus.cloud/docs/using-ludus/sources).

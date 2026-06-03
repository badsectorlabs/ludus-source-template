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
| Ansible roles    | `roles/<name>/`      | User-scoped; `--global-roles` for instance-wide | [roles/](roles/README.md)           |

A blueprints-only source, a roles-only source, and a templates-only source are all valid.

## Layout

```
LICENSE                              MIT placeholder; replace with your own
source.yml                           repo metadata (see below)
scripts/validate.py                  manifest schema check; extend with your own rules
.github/workflows/validate.yml       GitHub Actions: runs scripts/validate.py on every push
.gitlab-ci.yml                       GitLab CI: runs scripts/validate.py on every push

blueprints/                          blueprints + their dependencies — see blueprints/README.md
templates/                           Packer templates — see templates/README.md
roles/                               Ansible roles — see roles/README.md
```

`scripts/validate.py` and the two CI workflows ship a basic manifest check out of the box — it confirms your manifests parse and references resolve. If your org has its own CI conventions, delete `scripts/` and `.github/workflows/validate.yml` (and/or `.gitlab-ci.yml`) and wire in your own; nothing else in the template depends on them.

## source.yml

Repo-level metadata at the source root, and the whole file is optional — when absent, Ludus derives the name from the URL and the homepage from the git remote. Only `manifest_version` is required when the file is present (leave it at `1`); `name`, `description`, `authors`, `homepage`, and `license` are optional. `authors`, `homepage`, and `license` apply to every blueprint in the source. The example is annotated inline.

## More

Full reference: [Sources](https://docs.ludus.cloud/docs/using-ludus/sources).

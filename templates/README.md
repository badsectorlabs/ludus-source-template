# Packer templates

Each `templates/<name>/` directory is a standard Ludus Packer template, the same shape as the templates in the [Bad Sector Labs source](https://github.com/badsectorlabs/ludus-source-bsl/tree/main/templates):

```
templates/my-debian-base/
├── my-debian-base.pkr.hcl   the Packer build config (incl. a `description` variable)
├── template.yml             optional: a thumbnail for the catalog
├── http/                    Linux: preseed.cfg / kickstart served at install time
└── Autounattend.xml         Windows only: unattended install answer file
```

Templates install into each installing user's own Packer directory — so they survive Ludus server updates — and are keyed by the template's `*-template` name (the `vm_name` in the `.pkr.hcl`, not the folder name). A name that matches an already-installed or built-in template is skipped rather than overwritten, so prefix names you expect to share with your source slug (`bsl-debian-base`, not `debian-base`).

After `ludus source add`, run `ludus templates build` to produce the VM image.

## Catalog description

Give the template a one-line description for the catalog (`ludus source list`) with a static `description` variable in the `.pkr.hcl`, so it lives with the template instead of in a separate file:

```hcl
variable "description" {
  type    = string
  default = "Debian 12 (Bookworm) minimal x64 server."
}
```

Packer requires a variable's `default` to be a literal, so this stays a plain static string — unlike `template_description`, which is a build-time `local` (it carries an `isotime` stamp and is the Proxmox template's own notes, not a catalog blurb). If you'd rather keep the description in a separate file, a `description:` in `template.yml` still works as a fallback.

## template.yml (optional)

`template.yml` is optional and today only carries a thumbnail:

```yaml
thumbnail: logo.png        # a square transparent PNG bundled in this dir
```

`manifest_version` is optional — Ludus defaults it to 1, and you only need to set it once a future breaking schema requires it.

`thumbnail` is a **relative path** to a logo image bundled in this template dir (e.g. `thumbnail: logo.png`). Ludus stores it on the template's record; the GUI shows it on template cards, falling back to a built-in OS glyph when absent. Use a **square, transparent PNG** (256×256 works well) and keep it legible small — it renders as little as 24px. Raster only (PNG/JPEG/GIF/WebP); SVG is not accepted.

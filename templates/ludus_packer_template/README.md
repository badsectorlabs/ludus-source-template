# Ludus Packer Template Starter

A working, buildable [Ludus](https://ludus.cloud) VM template — minimal Debian 13 — meant to be copied and made your own. Copy this directory, rename one variable, add your customization, and you have a custom template your whole range can build VMs from.

## Quick start

Build it unchanged first, so you know your loop works:

```bash
ludus templates add -d .    # run from inside this directory
ludus templates build -n custom-debian-13-x64-template
ludus templates logs -f     # watch the build (~10 min)
```

Once built, any VM in a range config can use it:

```yaml
ludus:
  - vm_name: "{{ range_id }}-custom1"
    hostname: "{{ range_id }}-custom1"
    template: custom-debian-13-x64-template
    vlan: 10
    ip_last_octet: 10
    ram_gb: 4
    cpus: 2
    linux: true
```

Default credentials: `debian` / `debian`.

## Make it yours

1. **Rename it** — change `vm_name` in [`template.pkr.hcl`](template.pkr.hcl). That's the name users reference in range configs; keep the `-template` suffix.
2. **Bake things in** — add tasks to [`ansible/customize.yml`](ansible/customize.yml) (commented examples inside). It runs once at build time; everything it installs is inherited by every VM cloned from the template. Rule of thumb: bake in what *every* VM should have, leave per-VM setup to [Ludus roles](https://docs.ludus.cloud/docs/developers/ansible-roles).
3. **Adjust the knobs** — `vm_disk_size`, `vm_memory`, `vm_cpu_cores`, `description`.
4. **Optional icon** — drop an `icon.png` next to the `.pkr.hcl` and Ludus shows it in the catalog.

Iterate with:

```bash
ludus templates add -d . --force   # push your edits to the server
ludus templates build -n <your-template-name>
ludus templates logs -f
```

### A different OS entirely

Swap `iso_url`/`iso_checksum`, replace `http/preseed.cfg`, and adapt `boot_command`. Don't do this from scratch — copy the relevant pieces from a [known-good template](https://github.com/badsectorlabs/ludus-source-bsl/tree/main/templates) (Windows with autounattend + virtio drivers, Rocky, Ubuntu, Kali, …). The full authoring reference lives in [Creating your own templates for Ludus](https://docs.ludus.cloud/docs/using-ludus/templates/#creating-your-own-templates-for-ludus).

## How it works (60 seconds)

- A Ludus template directory is one `*.pkr.hcl` file plus supporting files. `ludus templates add -d .` uploads it; `ludus templates build` runs Packer on the Ludus server, which installs the OS from the ISO, runs the customize playbook, and saves the result as a Proxmox template.
- The **required Ludus variables block** in `template.pkr.hcl` (marked, don't remove) is how Ludus injects server-specific values at build time — storage pools, Proxmox credentials, the NAT interface. See the full list in [Creating your own templates for Ludus](https://docs.ludus.cloud/docs/using-ludus/templates/#creating-your-own-templates-for-ludus).
- VMs in ranges are *clones* of the built template: builds are slow-once, deploys are fast-always.

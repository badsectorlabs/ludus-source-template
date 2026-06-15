# =============================================================================
# Ludus Packer template starter
#
# This file builds a minimal Debian 13 VM template on your Ludus server.
# It works as-is — build it first, then make it yours:
#
#   1. Change `vm_name` below. That is the name users put in their range
#      config's `template:` key. Keep the `-template` suffix (Ludus convention,
#      and it helps Ludus infer the OS from the name).
#   2. Bake software/config into the image via ansible/customize.yml.
#   3. Adjust the sizing knobs (disk/memory/cores) and `description`.
#
# A Ludus template directory = one *.pkr.hcl file (the `.pkr.` part of the
# file name is required) plus any supporting files (preseed, scripts,
# playbooks, an optional icon.png shown in the catalog).
# =============================================================================

# --- Template knobs — edit these ---------------------------------------------

variable "vm_name" {
  type    = string
  default = "custom-debian-13-x64-template" # the name users reference; keep the -template suffix
}

variable "description" {
  type    = string
  default = "Customized Debian 13 (Trixie) x64 server."
}

variable "iso_url" {
  type    = string
  default = "https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-13.5.0-amd64-netinst.iso"
}

variable "iso_checksum" {
  type    = string
  default = "sha512:b2be60c555e328b4fa5ebb2d0e5c7ee6bc3eb4250c4dcfd3f78b8d9aec596efdf9f14f10a898c280eb252d50bbac91ea0a2bba29736df0d4985d50d4c8d77519"
}

variable "vm_cpu_cores" {
  type    = string
  default = "2"
}

variable "vm_disk_size" {
  type    = string
  default = "60G"
}

variable "vm_memory" {
  type    = string
  default = "4096"
}

# Credentials created by http/preseed.cfg. If you change them there, change
# them here too. Ludus convention is localuser:password unless there is a
# reason not to; this starter keeps debian:debian to match the stock Debian
# templates.
variable "ssh_username" {
  type    = string
  default = "debian"
}

variable "ssh_password" {
  type    = string
  default = "debian"
}

# Proxmox guest OS type: l26 = Linux 2.6+. Use win10/win11 etc. for Windows.
variable "os" {
  type    = string
  default = "l26"
}

# Optional catalog icon: drop an icon.png next to this file and Ludus picks
# it up when the template is registered.
variable "icon_path" {
  type    = string
  default = "icon.png"
}

# --- Required Ludus block — do not remove ------------------------------------
# Ludus sets these dynamically at build time (storage pools, Proxmox
# credentials, the NAT interface templates build on). Every .pkr.hcl file
# must declare them or packer can't receive the values.
variable "proxmox_url" {
  type = string
}
variable "proxmox_host" {
  type = string
}
variable "proxmox_username" {
  type = string
}
variable "proxmox_password" {
  type      = string
  sensitive = true
}
variable "proxmox_storage_pool" {
  type = string
}
variable "proxmox_storage_format" {
  type = string
}
variable "proxmox_skip_tls_verify" {
  type = bool
}
variable "proxmox_pool" {
  type = string
}
variable "iso_storage_pool" {
  type = string
}
variable "ansible_home" {
  type = string
}
variable "ludus_nat_interface" {
  type = string
}
####

locals {
  template_description = "${var.description} Built ${legacy_isotime("2006-01-02 03:04:05")}. username:password => ${var.ssh_username}:${var.ssh_password}"
}

source "proxmox-iso" "custom" {
  # Boots the Debian installer and points it at http/preseed.cfg for a fully
  # automated install. Swapping OS = new ISO + new preseed/autounattend +
  # new boot_command (copy a working one for your OS from
  # https://github.com/badsectorlabs/ludus-source-bsl/tree/main/templates).
  boot_command = [
    "<down><tab>", # non-graphical install
    "preseed/url=http://{{ .HTTPIP }}:{{ .HTTPPort }}/preseed.cfg ",
    "language=en locale=en_US.UTF-8 ",
    "country=US keymap=us ",
    "hostname=debian13 domain=local ",
    "<enter><wait>",
  ]
  boot_key_interval = "100ms"
  http_directory    = "./http"

  boot_iso {
    type              = "ide"
    iso_checksum      = "${var.iso_checksum}"
    iso_url           = "${var.iso_url}"
    iso_storage_pool  = "${var.iso_storage_pool}"
    iso_download_pve  = true
    unmount           = true
    keep_cdrom_device = false
  }

  communicator = "ssh"
  cores        = "${var.vm_cpu_cores}"
  cpu_type     = "host" # pass through the host CPU for max performance

  # virtio-scsi-single + io_thread + discard is the recommended disk setup
  # for Proxmox guests: io_thread gives >15% gains at low queue depth and
  # discard lets Proxmox reclaim space when files are deleted.
  scsi_controller = "virtio-scsi-single"
  disks {
    disk_size    = "${var.vm_disk_size}"
    format       = "${var.proxmox_storage_format}"
    storage_pool = "${var.proxmox_storage_pool}"
    type         = "virtio"
    discard      = true
    io_thread    = true
  }

  # virtio is paravirtualized and much faster than the emulated e1000; use it
  # whenever the guest has virtio drivers (Linux does out of the box).
  network_adapters {
    bridge = "${var.ludus_nat_interface}"
    model  = "virtio"
  }

  pool                     = "${var.proxmox_pool}"
  insecure_skip_tls_verify = "${var.proxmox_skip_tls_verify}"
  memory                   = "${var.vm_memory}"
  node                     = "${var.proxmox_host}"
  os                       = "${var.os}"
  password                 = "${var.proxmox_password}"
  proxmox_url              = "${var.proxmox_url}"
  template_description     = "${local.template_description}"
  username                 = "${var.proxmox_username}"
  vm_name                  = "${var.vm_name}"
  ssh_password             = "${var.ssh_password}"
  ssh_username             = "${var.ssh_username}"
  ssh_wait_timeout         = "30m"
  task_timeout             = "20m" // On slow disks the imgcopy operation takes > 1m
}

build {
  sources = ["source.proxmox-iso.custom"]

  # Runs once at template build time — everything it installs is baked into
  # the image and inherited by every VM cloned from it. Put your
  # customization in ansible/customize.yml.
  provisioner "ansible" {
    playbook_file      = "ansible/customize.yml"
    use_proxy          = false
    user               = "${var.ssh_username}"
    extra_arguments    = ["--extra-vars", "{ansible_python_interpreter: /usr/bin/python3, ansible_password: ${var.ssh_password}, ansible_sudo_pass: ${var.ssh_password}}"]
    ansible_env_vars   = ["ANSIBLE_HOME=${var.ansible_home}", "ANSIBLE_LOCAL_TEMP=${var.ansible_home}/tmp", "ANSIBLE_PERSISTENT_CONTROL_PATH_DIR=${var.ansible_home}/pc", "ANSIBLE_SSH_CONTROL_PATH_DIR=${var.ansible_home}/cp"]
    skip_version_check = true
  }
}

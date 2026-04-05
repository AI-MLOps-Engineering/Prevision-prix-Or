locals {
  # Dépôt public : https://github.com/AI-MLOps-Engineering/Prevision-prix-Or
  official_public_repo_url = "https://github.com/AI-MLOps-Engineering/Prevision-prix-Or.git"
  effective_repo_url       = trimspace(var.repo_url) != "" ? trimspace(var.repo_url) : local.official_public_repo_url
  git_clone_url = var.git_pat == "" ? local.effective_repo_url : replace(
    local.effective_repo_url,
    "https://github.com/",
    "https://x-access-token:${var.git_pat}@github.com/"
  )
}

resource "scaleway_instance_ip" "public_ip" {}

resource "scaleway_instance_server" "server" {
  name  = var.instance_name
  type  = var.instance_type
  image = "ubuntu_jammy"

  ip_id = scaleway_instance_ip.public_ip.id

  root_volume {
    size_in_gb = 120
  }

  user_data = {
    "cloud-init" = <<-EOT
#cloud-config
package_update: false
package_upgrade: false

write_files:
  - path: /root/.gold-repo-url
    permissions: '0600'
    content: |-
      ${local.git_clone_url}

  - path: /root/gold-bootstrap.sh
    permissions: '0755'
    encoding: b64
    content: ${filebase64("${path.module}/gold-bootstrap.sh")}

runcmd:
  - [ /bin/bash, /root/gold-bootstrap.sh ]

users:
  - name: root
    ssh_authorized_keys:
      - ${jsonencode(trimspace(var.ssh_public_key))}
EOT
  }
}

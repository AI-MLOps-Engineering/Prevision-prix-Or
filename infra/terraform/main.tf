terraform {
  required_providers {
    scaleway = {
      source  = "scaleway/scaleway"
      version = ">= 2.31.0"
    }
  }
}

provider "scaleway" {
  access_key = var.scw_access_key
  secret_key = var.scw_secret_key
  project_id = var.scw_project_id
  zone       = "fr-par-1"
  region     = "fr-par"
}

# ---------------------------------------------------------
# 1) Instance Scaleway
# ---------------------------------------------------------
# --- variables attendues (exemples) ---
# variable "instance_name" { type = string }
# variable "instance_type" { type = string }
# variable "scw_project_id" { type = string }
# variable "ssh_public_key" { type = string }

# Crée la clé SSH côté IAM (optionnel)
resource "scaleway_iam_ssh_key" "deploy_key" {
  name       = "${var.instance_name}-ssh"
  public_key = var.ssh_public_key
}

# Réserve une IP publique
resource "scaleway_instance_ip" "public_ip" {
  project_id = var.scw_project_id
}

# Crée le serveur SANS user_data (on l'attache ensuite via scaleway_instance_user_data)
resource "scaleway_instance_server" "server" {
  name  = var.instance_name
  type  = var.instance_type
  image = "ubuntu_jammy"

  root_volume {
    size_in_gb = 40
  }

  # attacher l'IP réservée (attribut ip_id présent dans ton provider)
  ip_id = scaleway_instance_ip.public_ip.id

  # autres champs éventuels : tags, security_group_ids, volumes, etc.
  tags = ["gold", "mlops", "api", "streamlit"]
}

# Crée le user_data (cloud-init) et l'attache au serveur existant ou si pas de serveur existant on le créé
resource "scaleway_instance_user_data" "cloudinit" {
  key       = "cloud-init"
  server_id = scaleway_instance_server.server.id
  value     = <<-EOT
    #cloud-config
    package_update: true
    packages:
      - apt-transport-https
      - ca-certificates
      - curl
      - gnupg
      - lsb-release
      - git
    runcmd:
      - set -e
      # Install Docker (official repo)
      - mkdir -p /etc/apt/keyrings
      - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
      - chmod a+r /etc/apt/keyrings/docker.gpg
      - echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
      - apt-get update -y
      - apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
      - systemctl enable --now docker
      # Clone repo and start compose
      - rm -rf /root/Prevision-prix-Or || true
      - git clone ${var.repo_url} /root/Prevision-prix-Or
      - cd /root/Prevision-prix-Or/infra
      - /usr/bin/docker compose up -d --build
      # Create systemd unit to ensure compose runs after reboot
      - cat > /etc/systemd/system/myapp-docker.service <<'EOF'
        [Unit]
        Description=Start myapp docker compose
        After=docker.service
        Requires=docker.service

        [Service]
        Type=oneshot
        WorkingDirectory=/root/Prevision-prix-Or/infra
        ExecStart=/usr/bin/docker compose up -d --build
        RemainAfterExit=yes

        [Install]
        WantedBy=multi-user.target
        EOF
      - systemctl daemon-reload
      - systemctl enable --now myapp-docker.service
  EOT

  depends_on = [
    scaleway_instance_server.server
  ]
}

# ---------------------------------------------------------
# 2) Provisioning (installation Docker + docker-compose)
# ---------------------------------------------------------
resource "null_resource" "provision" {
  depends_on = [scaleway_instance_server.server]

  connection {
    type        = "ssh"
    host        = scaleway_instance_ip.public_ip.address
    user        = "root"
    private_key = file("${pathexpand("~/.ssh/id_ed25519")}")
  }

  provisioner "file" {
    source      = "provision.sh"
    destination = "/root/provision.sh"
  }

  provisioner "file" {
    source      = "../docker-compose.yaml"
    destination = "/root/docker-compose.yaml"
  }

  #  provisioner "remote-exec" {
  #    inline = [
  #      "chmod +x /root/provision.sh",
  #      "/root/provision.sh"
  #    ]
  #  }
}

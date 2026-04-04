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

# SSH key
resource "scaleway_iam_ssh_key" "deploy_key" {
  name       = "${var.instance_name}-ssh"
  public_key = var.ssh_public_key
}

# Public IP
resource "scaleway_instance_ip" "public_ip" {
  project_id = var.scw_project_id
}

# Server WITH cloud-init directly inside
resource "scaleway_instance_server" "server" {
  name  = var.instance_name
  type  = var.instance_type
  image = "ubuntu_jammy"

  ip_id = scaleway_instance_ip.public_ip.id

  # ROOT VOLUME ONLY — 120 GB
  root_volume {
    size_in_gb = 120
  }

  user_data = {
    cloud-init = <<-EOT
#cloud-config
package_update: true
package_upgrade: true

packages:
  - git
  - curl
  - ca-certificates
  - apt-transport-https
  - gnupg

runcmd:
  # Install Docker
  - curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
  - sh /tmp/get-docker.sh
  - systemctl enable docker
  - systemctl start docker

  # Install Docker Compose plugin
  - mkdir -p /usr/libexec/docker/cli-plugins
  - curl -SL "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-linux-x86_64" -o /usr/libexec/docker/cli-plugins/docker-compose
  - chmod +x /usr/libexec/docker/cli-plugins/docker-compose

  # Clone repo
  - rm -rf /root/Prevision-prix-Or || true
  - git clone ${var.repo_url} /root/Prevision-prix-Or

  # Build & run containers
  - cd /root/Prevision-prix-Or/infra
  - /usr/bin/docker compose up -d --build

  # Systemd service
  - |
    cat > /etc/systemd/system/myapp-docker.service <<'EOF'
    [Unit]
    Description=Start docker compose for gold forecasting
    After=docker.service
    Requires=docker.service

    [Service]
    Type=oneshot
    WorkingDirectory=/root/Prevision-prix-Or/infra
    ExecStart=/usr/bin/docker compose up -d
    RemainAfterExit=yes

    [Install]
    WantedBy=multi-user.target
    EOF

  - systemctl daemon-reload
  - systemctl enable --now myapp-docker.service

EOT
  }

  tags = ["gold", "mlops", "api", "streamlit"]
}

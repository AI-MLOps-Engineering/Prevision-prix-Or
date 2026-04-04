resource "scaleway_instance_server" "server" {
  name  = var.instance_name
  type  = var.instance_type
  image = "ubuntu_jammy"

  ip_id = scaleway_instance_ip.public_ip.id

  root_volume {
    size_in_gb = 120
  }

  user_data = <<-EOT
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
  - curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
  - sh /tmp/get-docker.sh
  - systemctl enable docker
  - systemctl start docker

  - mkdir -p /usr/libexec/docker/cli-plugins
  - curl -SL "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-linux-x86_64" -o /usr/libexec/docker/cli-plugins/docker-compose
  - chmod +x /usr/libexec/docker/cli-plugins/docker-compose

  - rm -rf /root/Prevision-prix-Or || true
  - git clone ${var.repo_url} /root/Prevision-prix-Or

  - cd /root/Prevision-prix-Or/infra
  - /usr/bin/docker compose up -d --build

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

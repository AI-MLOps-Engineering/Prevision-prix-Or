#!/bin/bash
set -euxo pipefail
umask 077
exec >> /var/log/gold-bootstrap.log 2>&1
echo "gold-bootstrap start $(date -Is)"

REPO=$(tr -d ' \n\r' < /root/.gold-repo-url)
test -n "$REPO"

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git curl ca-certificates apt-transport-https gnupg lsb-release

curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
sh /tmp/get-docker.sh
systemctl enable docker
systemctl start docker
docker version

ARCH=$(uname -m)
case "$ARCH" in
  x86_64) DC_ARCH=x86_64 ;;
  aarch64|arm64) DC_ARCH=aarch64 ;;
  *)
    echo "Architecture non supportée: $ARCH"
    exit 1
    ;;
esac
mkdir -p /usr/libexec/docker/cli-plugins
curl -fsSL "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-linux-${DC_ARCH}" \
  -o /usr/libexec/docker/cli-plugins/docker-compose
chmod +x /usr/libexec/docker/cli-plugins/docker-compose
docker compose version

rm -rf /root/Prevision-prix-Or
clone_ok=0
for attempt in 1 2 3 4 5 6; do
  echo "git clone tentative ${attempt}"
  if git clone "$REPO" /root/Prevision-prix-Or; then
    clone_ok=1
    break
  fi
  sleep 20
done
if [ "$clone_ok" -ne 1 ]; then
  echo "git clone a échoué après plusieurs tentatives"
  exit 1
fi
test -d /root/Prevision-prix-Or/.git

cd /root/Prevision-prix-Or/infra
docker compose -f docker-compose.yaml up -d --build

cat > /etc/systemd/system/myapp-docker.service <<'UNIT'
[Unit]
Description=Start docker compose for gold forecasting
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/root/Prevision-prix-Or/infra
ExecStart=/usr/bin/docker compose -f docker-compose.yaml up -d
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable myapp-docker.service
systemctl start myapp-docker.service

rm -f /root/.gold-repo-url
echo "gold-bootstrap done $(date -Is)"

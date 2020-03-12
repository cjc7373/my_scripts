#!/usr/bin/env bash

if [ `whoami` != "root" ];then
    echo "This script must be run as root."
    exit 1
fi

wget --no-check-certificate -cq -t3 -T60 -O "caddy" \
"https://github.com/caddyserver/caddy/releases/download/v2.0.0-beta.15/caddy2_beta15_linux_amd64"
if [ $? -eq 0 ]; then
    echo -e "[${green}Info${plain}] ${filename} download completed..."
fi

mv caddy /usr/bin/

groupadd --system caddy
useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy

if [ ! -d /etc/caddy ]; then
    mkdir -p /etc/caddy
fi
touch /etc/Caddyfile

cat > /etc/systemd/system/caddy.service << EOF
[Unit]
Description=Caddy Web Server
Documentation=https://caddyserver.com/docs/
After=network.target

[Service]
User=caddy
Group=caddy
ExecStart=/usr/bin/caddy run --config /etc/caddy/Caddyfile --adapter caddyfile --resume --environ
ExecReload=/usr/bin/caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
TimeoutStopSec=5s
LimitNOFILE=1048576
LimitNPROC=512
PrivateTmp=true
ProtectSystem=full
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable caddy
systemctl start caddy

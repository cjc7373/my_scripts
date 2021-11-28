#!/usr/bin/env bash

red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
plain='\033[0m'

if [ `whoami` != "root" ];then
    echo "This script must be run as root."
    exit 1
fi

wget --no-check-certificate -c -t3 -T60 -O "caddy" \
"https://github.com/caddyserver/caddy/releases/download/v2.0.0-beta.17/caddy2_beta17_linux_amd64"
if [ $? -eq 0 ]; then
    echo -e "[${green}Info${plain}] ${filename} download completed..."
fi
chmod +x caddy
mv caddy /usr/bin/

if [ ! -e /etc/caddy/Caddyfile ]; then
    groupadd --system caddy
    useradd --system \
        --gid caddy \
        --create-home \
        --home-dir /var/lib/caddy \
        --shell /usr/sbin/nologin \
        --comment "Caddy web server" \
        caddy

    mkdir -p /etc/caddy
    cat > /etc/caddy/Caddyfile << EOF
0.0.0.0:2020 {
    respond "Hello, world!"
}
EOF

    # Create log folder
    chmod 755 /root
    mkdir -p /root/caddy
    chown caddy /root/caddy

    cat > /etc/systemd/system/caddy.service <<- EOF
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

else
    systemctl restart caddy
fi
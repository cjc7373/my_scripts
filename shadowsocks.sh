#!/usr/bin/env bash
# This script is only for Ubuntu/Debian to install Shadowsocks and v2ray plugin.
# Make sure you are using at least Debian 8 or Ubuntu 16.10 and kernal version greater than 4.9.

red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
plain='\033[0m'

download() {
    local filename=${1}
    local cur_dir=`pwd`
    if [ -s ${filename} ]; then
        echo -e "[${green}Info${plain}] ${filename} [found]"
    else
        echo -e "[${green}Info${plain}] ${filename} not found, download now..."
        wget --no-check-certificate -c -t3 -T60 -O ${1} ${2}
        if [ $? -eq 0 ]; then
            echo -e "[${green}Info${plain}] ${filename} download completed..."
        else
            echo -e "[${red}Error${plain}] Failed to download ${filename}, please download it to ${cur_dir} directory manually and try again."
            exit 1
        fi
    fi
}

if [ `whoami` != "root" ];then
	echo "This script must be run as root."
	exit 1
fi

echo -e "[${green}Info${plain}] Latest version: ${green}${shadowsocks_libev_ver}${plain}"

# Set shadowsocks-libev config password
echo "Please input password for shadowsocks-libev:"
read shadowsockspwd
[ -z "${shadowsockspwd}" ] && echo "Please input password" && exit 1
echo
echo "---------------------------"
echo "password = ${shadowsockspwd}"
echo "---------------------------"
echo

# Set shadowsocks-libev config port
while true
do
dport=$(shuf -i 9000-19999 -n 1)
echo -e "Please enter a port for shadowsocks-libev [1-65535]"
read -p "(Default port: ${dport}):" shadowsocksport
[ -z "$shadowsocksport" ] && shadowsocksport=${dport}
expr ${shadowsocksport} + 1 &>/dev/null
if [ $? -eq 0 ]; then
    if [ ${shadowsocksport} -ge 1 ] && [ ${shadowsocksport} -le 65535 ] && [ ${shadowsocksport:0:1} != 0 ]; then
        echo
        echo "---------------------------"
        echo "port = ${shadowsocksport}"
        echo "---------------------------"
        echo
        break
    fi
fi
echo -e "[${red}Error${plain}] Please enter a correct number [1-65535]"
done

shadowsockscipher="aes-256-gcm"

# Set shadowsocks v2ray plugin web path
echo "Please input web path for shadowsocks v2ray-plugin:"
echo "Note: use the form of /api/"
read webpath
[ -z "${webpath}" ] && echo "Please input path" && exit 1
echo
echo "---------------------------"
echo "web path = ${webpath}"
echo "---------------------------"
echo

# install shadowsocks and v2ray-plugin
# -y的意义不明 大概是自动yes
apt -y update
apt -y install shadowsocks-libev

# Download v2ray-plugin from github
ver=""
while true; do
    ver=$(wget --no-check-certificate -qO- https://api.github.com/repos/shadowsocks/v2ray-plugin/releases/latest | grep 'tag_name' | cut -d\" -f4)
    if [ -z ${ver} ]; then
    	echo "Error: Get v2ray-plugin latest version failed, retrying..."
    	continue
   	fi
    plugin_ver="v2ray-plugin-linux-amd64-$(echo ${ver})"
    download_link="https://github.com/shadowsocks/v2ray-plugin/releases/download/${ver}/${plugin_ver}.tar.gz"
    break
done
download "${plugin_ver}.tar.gz" "${download_link}"
tar zxf ${plugin_ver}.tar.gz
mv v2ray-plugin_linux_amd64 /usr/bin/v2ray-plugin
rm ${plugin_ver}.tar.gz

if [ ! -d /etc/shadowsocks-libev ]; then
    mkdir -p /etc/shadowsocks-libev
fi
cat > /etc/shadowsocks-libev/config.json <<- EOF
{
    "server":"127.0.0.1",
    "server_port":${shadowsocksport},
    "password":"${shadowsockspwd}",
    "timeout":300,
    "method":"${shadowsockscipher}",
    "fast_open":true,
    "nameserver":"1.1.1.1",
    "mode":"tcp_and_udp",
    "plugin":"v2ray-plugin",
	"plugin_opts":"server;path=${webpath}"
}
EOF

cat >> /etc/caddy/Caddyfile << EOF
0.0.0.0 {
	encode zstd gzip
	log {
		output file /root/caddy/access.log
	}
	reverse_proxy https://bing.com
	reverse_proxy ${webpath} localhost:${shadowsocksport}
}
EOF

systemctl enable shadowsocks-libev
systemctl start shadowsocks-libev

# Setting BBR
param=$(sysctl net.ipv4.tcp_congestion_control | awk '{print $3}')
if [[ x"${param}" == x"bbr" ]]; then
    echo -e "${green}Info:${plain} TCP BBR has already been installed. nothing to do..."
else
    sed -i '/net.core.default_qdisc/d' /etc/sysctl.conf
	sed -i '/net.ipv4.tcp_congestion_control/d' /etc/sysctl.conf
	echo "net.core.default_qdisc = fq" >> /etc/sysctl.conf
	echo "net.ipv4.tcp_congestion_control = bbr" >> /etc/sysctl.conf
	sysctl -p >/dev/null 2>&1
	echo -e "${green}Info:${plain} Setting TCP BBR completed..."
fi

echo "script finished."

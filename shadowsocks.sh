#!/bin/bash
# This script is only for Ubuntu/Debian to install Shadowsocks and v2ray plugin
# Make sure you are using root. 
# Make sure you are using at lease Debian 8 or Ubuntu 16.10.

download() {
    local filename=${1}
    local cur_dir=`pwd`
    if [ -s ${filename} ]; then
        echo -e "[${green}Info${plain}] ${filename} [found]"
    else
        echo -e "[${green}Info${plain}] ${filename} not found, download now..."
        wget --no-check-certificate -cq -t3 -T60 -O ${1} ${2}
        if [ $? -eq 0 ]; then
            echo -e "[${green}Info${plain}] ${filename} download completed..."
        else
            echo -e "[${red}Error${plain}] Failed to download ${filename}, please download it to ${cur_dir} directory manually and try again."
            exit 1
        fi
    fi
}

# request root permission
sudo echo

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
cp v2ray-plugin_linux_amd64 /usr/bin/v2ray-plugin

if [ ! -d /etc/shadowsocks-libev ]; then
    mkdir -p /etc/shadowsocks-libev
fi
cat > /etc/shadowsocks-libev/config.json<<-EOF
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

systemctl enable shadowsocks-libev
systemctl start shadowsocks-libev

echo "script finished."

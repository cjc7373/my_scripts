echo "Starting... MAKE SURE TO RUN UNDER ROOT"

mkdir Uninstall-aliyun-service
chmod 777 Uninstall-aliyun-service
cd Uninstall-aliyun-service

wget http://update.aegis.aliyun.com/download/uninstall.sh
chmod +x uninstall.sh
./uninstall.sh

wget http://update.aegis.aliyun.com/download/quartz_uninstall.sh
chmod +x quartz_uninstall.sh
./quartz_uninstall.sh

pkill aliyun-service
rm -rf /etc/init.d/agentwatch /usr/sbin/aliyun-service
rm -rf /usr/local/aegis*
rm /usr/sbin/aliyun-service
rm /lib/systemd/system/aliyun.service

cd -
rm -rf Uninstall-aliyun-service

echo "Done!"

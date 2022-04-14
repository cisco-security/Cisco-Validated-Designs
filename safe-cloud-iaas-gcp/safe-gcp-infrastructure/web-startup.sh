#Pre-requisite packages
sudo yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
sudo yum -y install https://rpms.remirepo.net/enterprise/remi-release-7.rpm
sudo yum -y update
sudo yum install -y epel-release nginx wget unzip lsof ipset rsync yum-util
sudo yum install -y ipset httpd yum-utils awk grep unzip sed dmidecode openssl curl libcurl rpm flock iptables ip6tables

#Nginx config
cd /etc/nginx
sudo mv nginx.conf nginx.conf.backup
sudo gsutil cp gs://${bucket_name_here}/nginx.conf .

#Service Start
sudo systemctl restart nginx
sudo systemctl enable nginx

#commands to install tetration
sudo gsutil cp gs://${bucket_name_here}/tetration_installer_intgssopov_enforcer_linux_tuvok.sh .
chmod u+x tetration_installer_intgssopov_enforcer_linux_tuvok.sh
./tetration_installer_intgssopov_enforcer_linux_tuvok.sh

#commands to get secure endpoint and install it
wget -O ampConnector.rpm ${secure_endpoint_url}
sudo yum localinstall ampConnector.rpm -y


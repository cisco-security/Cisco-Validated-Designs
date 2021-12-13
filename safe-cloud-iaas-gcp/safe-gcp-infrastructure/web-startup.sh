sudo yum install -y epel-release nginx wget unzip lsof ipset

cd /etc/nginx
sudo mv nginx.conf nginx.conf.backup
sudo wget https://raw.githubusercontent.com/cisco-security/Cisco-Validated-Designs/master/safe-cloud-iaas-gcp/safe-gcp-infrastructure/nginx.conf

sudo systemctl restart nginx
sudo systemctl enable nginx

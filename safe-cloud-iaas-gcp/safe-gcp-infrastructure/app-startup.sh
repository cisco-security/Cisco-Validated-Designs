#Pre-requisite packages
sudo yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
sudo yum -y install https://rpms.remirepo.net/enterprise/remi-release-7.rpm
sudo yum -y update
sudo yum install -y wget unzip lsof ipset httpd rsync yum-utils awk grep unzip sed dmidecode openssl curl libcurl rpm flock ipset iptables ip6tables
sudo yum-config-manager --enable remi-php74
sudo yum -y install php php-cli php-fpm php-mysqlnd php-zip php-devel php-gd php-mcrypt php-mbstring php-curl php-xml php-pear php-bcmath php-json
sudo systemctl start httpd
sudo systemctl enable httpd
sudo setsebool -P httpd_can_network_connect 1

#Wordpress install
sudo wget https://wordpress.org/latest.tar.gz
tar -xzf latest.tar.gz
cd wordpress
sudo cp wp-config-sample.php wp-config.php

#replace ${} with the info from the SQL instance
sudo sed -i -E 's/username_here/${user}/g' ./wp-config.php
sudo sed -i -E 's/password_here/${password}/g' ./wp-config.php
sudo sed -i -E 's/database_name_here/${database}/g' ./wp-config.php
sudo sed -i -E 's/localhost/${host_ip}/g' ./wp-config.php
sudo rsync -avP * /var/www/html/
sudo chown -R apache:apache /var/www/html/*
sudo systemctl restart httpd

#commands to install Secure Endpoint
sudo gsutil cp gs://${bucket_name_here}/tetration_installer_intgssopov_enforcer_linux_tuvok.sh .
sudo chmod u+x tetration_installer_intgssopov_enforcer_linux_tuvok.sh
./tetration_installer_intgssopov_enforcer_linux_tuvok.sh

#commands to get secure endpoint and install it
wget -O ampConnector.rpm ${secure_endpoint_url}
sudo yum localinstall ampConnector.rpm -y

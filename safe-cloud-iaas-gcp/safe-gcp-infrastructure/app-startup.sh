sudo yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
sudo yum -y install https://rpms.remirepo.net/enterprise/remi-release-7.rpm
sudo yum -y update
sudo yum install -y wget unzip lsof ipset httpd rsync yum-utils
sudo yum-config-manager --enable remi-php74
sudo yum -y install php php-cli php-fpm php-mysqlnd php-zip php-devel php-gd php-mcrypt php-mbstring php-curl php-xml php-pear php-bcmath php-json
sudo systemctl start httpd
sudo systemctl enable httpd

sudo setsebool -P httpd_can_network_connect 1

sudo wget https://wordpress.org/latest.tar.gz
tar -xzf latest.tar.gz
cd wordpress
sudo cp wp-config-sample.php wp-config.php

sudo sed -i -E 's/username_here/${user}/g' ./wp-config.php
sudo sed -i -E 's/password_here/${password}/g' ./wp-config.php
sudo sed -i -E 's/database_name_here/${database}/g' ./wp-config.php
sudo sed -i -E 's/localhost/${host}/g' ./wp-config.php

sudo rsync -avP * /var/www/html/
sudo chown -R apache:apache /var/www/html/*
sudo systemctl restart httpd

#!/bin/bash

# Documentation to install DNG can be found here - https://duo.com/docs/dng

#Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum makecache fast
sudo yum install -y docker-ce
sudo systemctl enable docker.service
sudo systemctl start docker
sudo usermod -aG docker $(whoami)
sudo chmod 666 /var/run/docker.sock

#Docker Compose
sudo yum install -y wget
wget -O- "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" > ./docker-compose
chmod +x ./docker-compose
sudo mv ./docker-compose  /usr/local/bin/
docker-compose --version

#Duo Network Gateway
wget --content-disposition https://dl.duosecurity.com/network-gateway-latest.yml -O network-gateway.yml
docker-compose -p network-gateway -f network-gateway.yml up -d
docker ps

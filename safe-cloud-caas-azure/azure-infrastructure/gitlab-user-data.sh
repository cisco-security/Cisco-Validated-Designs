#!/bin/sh

# Documentation to install GitLab-CE can be found here - https://about.gitlab.com/install/?version=ce#ubuntu

#Install Docker CE
sudo apt-get -y update && sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get -y update && sudo apt-get -y install docker-ce docker-ce-cli containerd.io

#Install Gitlab CE
sudo apt-get -y install curl tzdata perl
curl -sS https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
sudo EXTERNAL_URL="http://safegitlab.${gitlabaddress}" apt-get install gitlab-ce

# Enable container registry- https://docs.gitlab.com/ee/administration/packages/container_registry.html
sudo echo "registry_external_url 'http://safegitlab.${gitlabaddress}:5050'" >> /etc/gitlab/gitlab.rb
sudo gitlab-ctl reconfigure

#Install Gitlab Runner
curl -LJO "https://gitlab-runner-downloads.s3.amazonaws.com/latest/deb/gitlab-runner_amd64.deb"
dpkg -i gitlab-runner_amd64.deb

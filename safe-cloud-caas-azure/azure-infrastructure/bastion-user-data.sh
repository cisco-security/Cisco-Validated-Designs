#!/bin/bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az version

curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client

curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh

sudo apt-add-repository ppa:git-core/ppa
sudo apt-get update
sudo apt-get -y install git
git clone https://github.com/cisco-security/Cisco-Validated-Designs.git /home/azureuser/Cisco-Validated-Designs

sudo apt install jq

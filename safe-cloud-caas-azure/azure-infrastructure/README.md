# Azure Infrastructure
![alt text](https://github.com/cisco-security/Cisco-Validated-Designs/blob/master/safe-cloud-caas-azure/images/Azure-Infra-0.svg)

## Azure Resources:  
This Terraform code provisions following resources:   
### Hub Resource Group
  - Azure VNets (CIDR - 10.10.0.0/16) with two subnets - (10.10.1.0/24 and 10.10.2.0/24).
  - UDR with appropriate routes
  - Bastion host in VNet1 (installed with utilities awscli, eksctl, kubectl, helm, Git client).
  - Virtual machine to install Duo Network Gateway (to be installed later)
  - AKS cluster with 2 nodes to install a private Gitlab instance (to be installed later).

### Spoke1 Resource Group
  - Azure VNets - (CIDR - 10.20.0.0/16).
  - UDR with appropriate routes
  - AKS cluster with three nodes in three availability zones.

### Spoke2 Resource Group
  - Azure VNets - (CIDR - 10.30.0.0/16).
  - UDR with appropriate routes
  - AKS cluster with three nodes in three availability zones.

### VNet Peering
  - The template provisions VNet peering link between Hub VNet and Spoke Vnets.

## Steps to deploy:  
  - clone this repo and follow the terraform script as show in snapshot

![alt text](https://github.com/amansin0504/aws-cloudnative-cvd/blob/main/aws-vpc-infrastructure/Images/tfmoutput.png)

# Azure Infrastructure
![alt text](https://github.com/cisco-security/Cisco-Validated-Designs/blob/master/safe-cloud-caas-azure/images/Azure-Infra-0.svg)

## Azure Resources:  
This Terraform code provisions following resources:   
### Hub Resource Group
  - Two Azure VNets - (CIDR - 10.10.0.0/16 and 10.11.0.0/16).
  - UDR with appropriate routes
  - Bastion host in VNet1 (installed with utilities awscli, eksctl, kubectl, helm, Git client).
  - Virtual machine to install Duo Network Gateway (to be installed later)
  - AKS cluster with 2 nodes to install a private Gitlab instance (to be installed later).

### Spoke1 Resource Group
  - Azure VNets - (CIDR - 10.20.0.0/16).
  - UDR with appropriate routes
  - AKS cluster with three nodes in three availability zones.

### Spoke2 Resource Group
  - Azure VNets - (CIDR - 10.20.0.0/16).
  - UDR with appropriate routes
  - AKS cluster with three nodes in three availability zones.

### VNet Peering
  - The template provisions VNet peering link between Hub VNet and Spoke Vnets.

## Steps to deploy:  
  - Upload all the files in this repo to an S3 bucket.  
  - Navigate to CloudFormation > Create Stack and add the Amazon S3 URL for master template file (create-vpc-architecture-master.yaml).  
  - Fill all the prompted details(include the name of S3 bucket with all the template files) and create the stack. The CloudFormation stack with deploy all the resources in a nested manner. A Sample run will look as below.  

![alt text](https://github.com/amansin0504/aws-cloudnative-cvd/blob/main/aws-vpc-infrastructure/Images/cfmstack.png)

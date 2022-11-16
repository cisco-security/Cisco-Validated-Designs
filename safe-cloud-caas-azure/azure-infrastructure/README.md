# Azure Infrastructure
![azure-topo](https://user-images.githubusercontent.com/10239022/202280924-bc697739-c6e0-471a-a6d6-eb564ab11e1d.svg)


## Azure Resources:  
Follow the [link](https://docs.microsoft.com/en-us/azure/developer/terraform/store-state-in-azure-storage?tabs=terraform#2-configure-remote-state-storage-account) to do the initial set up for provisioning Azure resources using Terraform. This Terraform code provisions following resources:  

### Hub Resource Group
  - Azure VNet (CIDR - 10.10.0.0/16) with two subnets - (10.10.1.0/24 and 10.10.2.0/24).
  - UDR with appropriate routes
  - HubSubnetA - Linux and Windows Bastion hosts (with utilities az cli, kubectl, helm and Git) and Duo Network Gateway Instance.
  - HubSubnetB - Private GitLab and GitLab Runner instance, Secure Workload Connector.

### Spoke1 Resource Group
  - Azure VNet - (CIDR - 10.20.0.0/16).
  - UDR with appropriate routes
  - AKS cluster with three nodes in three availability zones.

### VNet Peering
  - The template provisions VNet peering link between Hub VNet and Spoke VNets.

### Storage Accounts - Hub Resource Group
  - Azure Storage Accounts for storing NSG flow logs and lab files.

### Azure Container registry - Hub Resource Group
  - Azure Container registry for privately storing docker images.

## Steps to deploy:  
  - Clone this repository
  ```bash
  git clone https://github.com/cisco-security/Cisco-Validated-Designs.git
  cd Cisco-Validated-Designs/safe-cloud-caas-azure/azure-infrastructure
  ```
  - Provision the Azure resource using Terraform
  ```bash
  terraform apply
  ```

### Output:
![alt text](https://raw.githubusercontent.com/cisco-security/Cisco-Validated-Designs/master/safe-cloud-caas-azure/images/TerraformApply.png)

**_NOTE:_**  This repo contains terraform for single spoke resource group. If you wish to have two or more spokes then you can simply copy the spokes.tf as spokes1.tf, spokes2.tf...etc. and update the string 'spoke1' everywhere in the source with appropriate spoke name for example - replace spoke1RG and Spoke1VNet with spoke2RG and Spoke3VNet .

## Clean Up:
  - Delete the Azure resources
  ```bash
  terraform destroy
  ```

### Output:
![alt text](https://raw.githubusercontent.com/cisco-security/Cisco-Validated-Designs/master/safe-cloud-caas-azure/images/TerraformDestroy.png)

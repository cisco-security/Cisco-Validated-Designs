# AWS VPC Infrastructure
![alt text](https://github.com/amansin0504/aws-cloudnative-cvd/blob/main/aws-vpc-infrastructure/Images/AWS-Infra.png)

## AWS Resources:  
This CloudFormation stack provisions following resources:   
### Management VPC
  - The VPC is spread across two availability zones - (CIDR - 10.10.0.0/16).
  - Two public subnets - 10.10.10.0/24 in availability zone 1 and 10.10.20.0/24 in availability zone 2  
  - Two private subnets - 10.10.11.0/24 in availability zone 1 and 10.10.21.0/24 in availability zone 2  
  - NAT Gateways - One per availability zone for providing internet access to private subnets in each availability zone  
  - Internet Gateway attached to VPC.  
  - Private Route Tables - One for each availability zone with default route pointing to corresponding NAT Gateway.  
  - Public Route Tables - One route table associate to public subnets, default route points to Internet Gateway.  
  - Bastion hosts in each public subnet (installed with utilities awscli, eksctl, kubectl, helm, Git client).  

### Staging VPC
  - The VPC is spread across three availability zones - (CIDR - 10.20.0.0/16).  
  - Three public subnets - 10.20.10.0/24, 10.20.20.0/24 and 10.20.30.0/24 in availability zones 1,2 and 3 respectively.  
  - Three private subnets - 10.20.11.0/24, 10.20.21.0/24 and 10.20.31.0/24 in availability zones 1,2 and 3 respectively.  
  - NAT Gateways - One per availability zone for providing internet access to private subnets in each availability zone.  
  - Internet Gateway attached to VPC.  
  - Private Route Tables - One for each availability zone with default route pointing to corresponding NAT Gateways.  
  - Public Route Tables - One route table associate to public subnets, default route points to Internet Gateway.  

### Production VPC
  -  The VPC is spread across three availability zones - (CIDR - 10.30.0.0/16).  
  - Three public subnets - 10.30.10.0/24, 10.30.20.0/24 and 10.30.30.0/24 in availability zones 1,2 and 3 respectively.  
  - Three private subnets - 10.30.11.0/24, 10.30.21.0/24 and 10.30.31.0/24 in availability zones 1,2 and 3 respectively.  
  - NAT Gateways - One per availability zone for providing internet access to private subnets in each availability zone.   
  - Internet Gateway attached to VPC.  
  - Private Route Tables - One for each availability zone with default route pointing to corresponding NAT Gateways.  
  - Public Route Tables - One route table associate to public subnets, default route points to Internet Gateway.  

### VPC Peering
  - The template provisions a peering link between management VPC, staging VPC and management VPC, production VPC.
  - It also adds the necessary routes required for communication between the management, staging and production VPCs.  

## Steps to deploy:  
  - Request additional Elastic IP Addresses for the region being used in AWS. 5 is the current maximum without a ticket requesting more (11 needed if template is unmodified)
  - Upload all the files in this repo to an S3 bucket.  
  - Navigate to CloudFormation > Create Stack and add the Amazon S3 URL for master template file (create-vpc-architecture-master.yaml).  
  - Fill all the prompted details(include the name of S3 bucket with all the template files) and create the stack. The CloudFormation stack with deploy all the resources in a nested manner. A Sample run will look as below.  

![alt text](https://github.com/amansin0504/aws-cloudnative-cvd/blob/main/aws-vpc-infrastructure/Images/cfmstack.png)

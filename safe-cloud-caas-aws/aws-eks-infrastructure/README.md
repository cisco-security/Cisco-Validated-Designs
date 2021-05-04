# AWS EKS Infrastructure
![alt text](https://github.com/cisco-security/Cisco-Validated-Designs/blob/master/safe-cloud-caas-aws/aws-eks-infrastructure/images/AWS-Infra.png)

## Pre-Requisites:
These configuration files provision EKS clusters in existing VPC infrastructure. Refer to the aws-vpc-infrastructure directory within this repo to provision the required VPC resources before creating the EKS clusters.

## AWS Resources:  
These YAML manifests provision following three EKS clusters.

### create-mgmt-eks-cluster.yaml.yaml - creates a two node EKS Cluster in management VPC  
  - The VPC is spread across two availability zones - (CIDR - 10.10.0.0/16)
  - Two public subnets - 10.10.10.0/24 in availability zone 1 and 10.10.20.0/24 in availability zone 2  
  - Two private subnets - 10.10.11.0/24 in availability zone 1 and 10.10.21.0/24 in availability zone 2  

### create-staging-eks-cluster.yaml.yaml - creates a three node EKS Cluster in staging VPC  
  - The VPC is spread across three availability zones - (CIDR - 10.20.0.0/16).  
  - Three public subnets - 10.20.10.0/24, 10.20.20.0/24 and 10.20.30.0/24 in availability zones 1,2 and 3 respectively.  
  - Three private subnets - 10.30.11.0/24, 10.30.21.0/24 and 10.30.31.0/24 in availability zones 1,2 and 3 respectively.  

### create-production-eks-cluster.yaml.yaml - creates a three node EKS Cluster in production VPC    
  -  The VPC is spread across three availability zones - (CIDR - 10.30.0.0/16).  
  - Three public subnets - 10.30.10.0/24, 10.30.20.0/24 and 10.30.30.0/24 in availability zones 1,2 and 3 respectively.  
  - Three private subnets - 10.30.11.0/24, 10.30.21.0/24 and 10.30.31.0/24 in availability zones 1,2 and 3 respectively.

### Sample Run
eksctl create cluster --config-file create-staging-eks-cluster.yaml

```
[ℹ]  eksctl version 0.30.0
[ℹ]  using region us-west-2
[ℹ]  setting availability zones to [us-west-2a us-west-2c us-west-2c]
[ℹ]  subnets for us-west-2a - public:10.20.10.0/24 private:10.20.11.0/24
[ℹ]  subnets for us-west-2c - public:10.20.20.0/24 private:10.20.21.0/24
[ℹ]  subnets for us-west-2c - public:10.20.30.0/24 private:10.20.31.0/24
[ℹ]  using Kubernetes version 1.18
[ℹ]  creating EKS cluster "staging-eks" in "us-west-2" region with managed nodes
[ℹ]  1 nodegroup (staging-workers) was included (based on the include/exclude rules)
[ℹ]  will create a CloudFormation stack for cluster itself and 0 nodegroup stack(s)
[ℹ]  will create a CloudFormation stack for cluster itself and 1 managed nodegroup stack(s)
[ℹ]  if you encounter any issues, check CloudFormation console or try 'eksctl utils describe-stacks --region=us-west-2 --cluster=staging-eks'
[ℹ]  CloudWatch logging will not be enabled for cluster "staging-eks" in "us-west-2"
[ℹ]  you can enable it with 'eksctl utils update-cluster-logging --enable-types={SPECIFY-YOUR-LOG-TYPES-HERE (e.g. all)} --region=us-west-2 --cluster=staging-eks'
[ℹ]  Kubernetes API endpoint access will use default of {publicAccess=true, privateAccess=false} for cluster "staging-eks" in "us-west-2"
[ℹ]  2 sequential tasks: { create cluster control plane "staging-eks", 2 sequential sub-tasks: { 3 sequential sub-tasks: { associate IAM OIDC provider, 2 sequential sub-tasks: { create IAM role for serviceaccount "kube-system/aws-node", create serviceaccount "kube-system/aws-node" }, restart daemonset "kube-system/aws-node" }, create managed nodegroup "staging-workers" } }
[ℹ]  building cluster stack "eksctl-staging-eks-cluster"
[ℹ]  deploying stack "eksctl-staging-eks-cluster"
[ℹ]  building iamserviceaccount stack "eksctl-staging-eks-addon-iamserviceaccount-kube-system-aws-node"
[ℹ]  deploying stack "eksctl-staging-eks-addon-iamserviceaccount-kube-system-aws-node"
[ℹ]  serviceaccount "kube-system/aws-node" already exists
[ℹ]  updated serviceaccount "kube-system/aws-node"
[ℹ]  daemonset "kube-system/aws-node" restarted
[ℹ]  building managed nodegroup stack "eksctl-staging-eks-nodegroup-staging-workers"
[ℹ]  deploying stack "eksctl-staging-eks-nodegroup-staging-workers"
[ℹ]  waiting for the control plane availability...
[✔]  saved kubeconfig as "/Users/amansin3/.kube/config"
[ℹ]  no tasks
[✔]  all EKS cluster resources for "staging-eks" have been created
[ℹ]  nodegroup "staging-workers" has 2 node(s)
[ℹ]  node "ip-192-168-11-240.us-west-2.compute.internal" is ready
[ℹ]  node "ip-192-168-87-158.us-west-2.compute.internal" is ready
[ℹ]  waiting for at least 2 node(s) to become ready in "staging-workers"
[ℹ]  nodegroup "staging-workers" has 2 node(s)
[ℹ]  node "ip-192-168-11-240.us-west-2.compute.internal" is ready
[ℹ]  node "ip-192-168-87-158.us-west-2.compute.internal" is ready
[ℹ]  kubectl command should work with "/Users/amansin3/.kube/config", try 'kubectl get nodes'
[✔]  EKS cluster "staging-eks" in "us-west-2" region is ready
```  

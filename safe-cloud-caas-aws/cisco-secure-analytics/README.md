# Cisco Secure Cloud Analytics integration with AWS VPCs  
The template(aws-swc.template) provides first time Secure Cloud Analytics integration with a single AWS VPC. The integration happens in 3 steps.
  - Create an S3 bucket to store VPC flow logs  
  - Enable VPC flows logs on a given AWS VPC and deliver the flow logs to newly created S3 bucket  
  - Create an IAM role and associate IAM policies to it to allow Secure Cloud Analytics the permission to S3 bucket and other resources  

# Sample CloudFormation Run  
![alt text](https://github.com/cisco-security/Cisco-Validated-Designs/blob/master/safe-cloud-caas-aws/cisco-secure-analytics/images/step1.png)  
![alt text](https://github.com/cisco-security/Cisco-Validated-Designs/blob/master/safe-cloud-caas-aws/cisco-secure-analytics/images/step2.png)  

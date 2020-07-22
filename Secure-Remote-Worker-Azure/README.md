This sample Azure Resource Manager (ARM) template helps you deploy Cisco ASAv in an availability zone (AZ) inside your Azure VNet. 

Step1: Use ASA1-az1.json ARM template to deploy hubasa1 in AZ1.
Step2: Use parametersFileASA1.json.
Step3: Customize it to deploy additional ASAs in other AZs. 
Step4: Modify the ASA1-az1.json template, save it as and ASA2-az2.json - replace zone 1 to zone 2 to deploy hubasa2 in AZ2.
Step5: Modify the ASA1-az1.json template, save it as and ASA3-az3.json - replace zone 1 to zone 3 to deploy hubasa3 in AZ3.

Note: This is just a sample ARM template and not customized from the customer's network, may not work in a production network without proper customization and tweaking. Use this template as a starting point to help you build your ARM template.

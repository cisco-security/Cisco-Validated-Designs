# aws-cloud-formation-tiered-network-config

This repo contains an example template that can be used to create a tiered network in AWS using cloud formation.

It has a master template that calls nested stacks for each portion of the network.

It also has a single file that can be used instead of the nested setup. This readme will go over how to use the nested-stack and how to make it your own.

# What is CloudFormation

CloudFormation is an automation and expandability service provided by AWS. It allows users to specify resources within AWS in either a JSON or YAML file and then have it created in AWS. For example, if someone wants to make a VM, they can specify in the file they want a VM with a certain OS. Then upload the file into CloudFormation and CloudFormation will read the file and create the VM with no further input needed from the user.

It can be used to update something after it has been created as well. With our previous VM example, say we want to add the VM to a certain subnet. We can add a subnet assignment section to the same file and CloudFormation will see a change has been made to the file and perform an update. It will skip the VM section since no change was made, but it will do the subnet assignment since that is new.

The processes above are called _stacks_. So, each time a resource is created, it is made within a stack. Within each stack we can make what is called a nested stack. This is when we reference a separate configuration file within another one. We do not need to use nested stacks, but it makes reading the configurations easier and reduces development time of the stacks. This is because we are not using one large file that could be error prone. It allows us to develop each section separately and not have a single point of failure.

This guide will break down how we achieved this setup and how it works. As we get to a new portion of the file, we will go over how we share resources within files, how they are called, and what is happening.

# What will be created with this setup?

With these configuration files, we will be building out a 3-tiered architecture setup using a nested stack setup. The architecture will look like so:

![architecture-diagram](https://user-images.githubusercontent.com/10239022/116435534-770e3280-a819-11eb-8d62-2db785b36d89.jpeg)

The architecture consists of a web tier that lives in a public subnet, an application tier that is in a private subnet, and a database tier that is in another private subnet. The web tier has an application load balancer that will balance requests between multiple hosts within the subnet. Then each host in the web application tier will reach out to a load balancer for the application tier. This load balancer will do the same thing as the web balancer but for the application hosts. Then the application hosts will reach out the database without a load balancer. This database lives in both subnets but is a single instance. The end goal of this setup is to have a running web application utilizing this architecture.

# Initial Setup

To get this setup working, we first need to make a S3 bucket and make it publicly accessible. This will not make the whole bucket publicly accessible, but it does allow us to pick and choose what files can be publicly accessed. Once the bucket has been created we need to download all the files from the repo including the web config files.

Then we need to upload all of the files into this S3 bucket. Once they are uplaoded, we only need to make two of the files publicly accesible. Those two files are the web-config files. The wordpress config and the nginx config. Once that has been finished, we need to update all of the teamplate files URL for the templates to be the URL of the file in AWS.

For each template URL in the resources section of the masterTemplate, we will have a "change-me-filename-s3-url" where the filename will be the nake of each file. This will let us know which S3 file URL needs to be used. Additionally, we need to update the wget URLs for the user data scripts in the two launch configs. Those will be set to "changeme-nginx-url" in the web launch config file and "changeme-wordpress-url" for the app launch config file. Once those updates have been completed, we just need to re-upload the two launch config files.

# Nested stack configuration files

To access the nested stack files, you can go to the nested stack directory in this repo. Within that directory there are 8 files in total. The _masterTemplate.json_ is the template you will use to run all the subsequent json files in this folder.

Each configuration file is numbered in the order that the master template calls them:

- 1-network-setup
- 2-db-setup
- 2-swc-setup
- 3-app-launch-config
- 4-app-asg-lb
- 5-web-launch-config
- 6-web-asg-lb
- masterTemplate

Each number for each file is the step at which they take place in the master template. You can see that there are two step **2** files. One for the database and one for stealthwatch. This means that they do not rely on another portion of the configuration to be finished before another one can start. All of the rest that continue the numbering depend on one of the others before it.

# Master Template Overview

The master template has three main sections in it.

1. Description
2. Mappings
3. Parameters
4. Resources

## Description

The description is a blurb of what the template is for so that anyone reading it will be able to tell its use.

## Mappings

Mappings are used to define what resource should be used in which region of AWS. For example: an AWS VM(AMI) will have separate IDs depending on the region it is in. We can use the mappings to say, "use this AMI if in us-east-1 or use this AMI if in ap-northeast-1".

For each region we define, we want to specify the virtualization type and the AMI ID. The virtualization type is generally decided by what the AMI was created for, but sometimes you can have multiple types for one AMI. This is why we have to specify which type we want to look for.

```json
"Mappings": {
    "RegionMap": {
      "us-east-1": { "HVM": "ami-00e87074e52e6c9f9" },
      "us-west-1": { "HVM": "ami-0bdb828fd58c52235" },
      "eu-west-1": { "HVM": "ami-08d2d8b00f270d03b" },
      "ap-southeast-1": { "HVM": "ami-0adfdaea54d40922b" },
      "ap-northeast-1": { "HVM": "ami-0ddea5e0f69c193a4" }
    }
  }
```

## Parameters

The parameters are values that are to be passed into the template when it is run in CloudFormation. Parameters can be a name for S3 Bucket (file storage) or a cidr block for a subnet and many other things can be passed into it. Parameters look like so within the file:
![image](https://user-images.githubusercontent.com/10239022/114605903-924d3f80-9c68-11eb-9ad6-7e9337578c54.png)

These same parameters that are defined in the file will show up when you attempt to create a stack in CloudFormation like so:
![image](https://user-images.githubusercontent.com/10239022/114731629-e7905c00-9d0f-11eb-87af-dbff6055f3c3.png)

We do not need to use parameters, but it makes the setup more dynamic and allows the use of the files without needing to manually change the fields in the file each time we want something to be different.

In our parameters section we have a multitude of inputs. There are inputs for the subnets, availability zones, names for the database and S3 bucket, types for the instances (t2.mirco/m2.medium)., and a username/password for the database.

We will go over these parameters since most of them are repeated with different names:

- CidrBlock
- DBInstanceID
- DBName
- DBInstanceClass
- DBAllocatedStorage
- DBUsername
- DBPassword
- AppAMItype
- appKeyName
- S3BucketName
- ExternalID
- AvailabilityZone1

Within each parameter we go over, we will put the parameter in a code block and break it down. For the AMI type parameters, we will shorten them because they are very large.

<details><summary><h4 style="display:inline">CidrBlock</h4></summary>
<p>
CidrBlock is used to define the subnet to be used for the VPC being created.  It is repeated for each smaller subnet that will be used within the template(OutsideNet, InsideNet, DBNet). 
      
```json
"CidrBlock": {
      "AllowedPattern": "((\\d{1,3})\\.){3}\\d{1,3}/\\d{1,2}",
      "Default": "10.0.0.0/16",
      "Description": "VPC CIDR Block (e.g., 10.0.0.0/16)",
      "Type": "String"
    }
```

The CidrBlock parameter has four parameters.

- **AllowedPattern** - This contains a regex to allow certain text to be entered into the input.
- **Default** - This is used to make have the input load with a default value. In this case it is a whole subnet.
- **Description** - This contains an explanation of what the input is used for or what should be input.
- **Type** - _REQUIRED_ - This field is required and determines how it will be interpreted as a parameter. Since it is of type string, it will be an input box when looking at the parameter section in CloudFormation. For other parameters it could be a dropdown, but this is determined by the type.

Since we have gone over AllowedPattern, Default, and Description we will not go over them again unless there is a major change in them. But for the most part the values will change, but the concept will remain the same.

</p>
</details>

<details><summary><h4 style="display:inline">DBInstanceID</h4></summary>
<p>
This field is used to name the identifier when it is created. The identifier is used as the true name of the database when referencing it.
      
```json
"DBInstanceID": {
      "Default": "mydbinstance",
      "Description": "My database instance",
      "Type": "String",
      "MinLength": "1",
      "MaxLength": "63",
      "AllowedPattern": "[a-zA-Z][a-zA-Z0-9]*",
      "ConstraintDescription": "Must begin with a letter and must not end with a hyphen or contain two consecutive hyphens."
    }
```

- **MinLength** - This ensures the field is not left empty.
- **MaxLength** - The ensures the field does not have too many characters.
- **ConstraintDescription** - This is used to tell a user that there are requirements when creating this field.
</p>
</details>

<details><summary><h4 style="display:inline">DBName</h4></summary>
<p>
This field is used to name the database.  It’s used as an easy to find name for us to use.
      
```json
"DBName": {
      "Default": "mydb",
      "Description": "My database",
      "Type": "String",
      "MinLength": "1",
      "MaxLength": "64",
      "AllowedPattern": "[a-zA-Z][a-zA-Z0-9]*",
      "ConstraintDescription": "Must begin with a letter and contain only alphanumeric characters."
    }
  ```

</p>
</details>

<details><summary><h4 style="display:inline">DBInstanceClass</h4></summary>
<p>
This field is used to determine the class type to be used.  This determine show much ram and CPU it will have on hand.
      
```json
"DBInstanceClass": {
      "Default": "db.m5.large",
      "Description": "DB instance class",
      "Type": "String",
      "ConstraintDescription": "Must select a valid DB instance type."
    }
  ```

</p>
</details>

<details><summary><h4 style="display:inline">DBAllocatedStorage</h4></summary>
<p>
This field will be used to determine the size of the database.
      
```json
"DBAllocatedStorage": {
      "Default": "50",
      "Description": "The size of the database (GiB)",
      "Type": "Number",
      "MinValue": "5",
      "MaxValue": "1024",
      "ConstraintDescription": "must be between 20 and 65536 GiB."
    }
  ```
  
* **Type** - The type for this parameter is Number instead of string.  This means it will only take a number (0-9).
</p>
</details>

<details><summary><h4 style="display:inline">DBUsername</h4></summary>
<p>
This field is to name the user that will be used to access the database.
      
```json
"DBUsername": {
      "Description": "Username for MySQL database access",
      "Type": "String",
      "MinLength": "1",
      "MaxLength": "16",
      "AllowedPattern": "[a-zA-Z][a-zA-Z0-9]*",
      "ConstraintDescription": "must begin with a letter and contain only alphanumeric characters."
    }
```

</p>
</details>

<details><summary><h4 style="display:inline">DBPassword</h4></summary>
<p>
This field is used to create a password for the database user being created.
      
```javascript
"DBPassword": {
      "NoEcho": "true",
      "Description": "Password MySQL database access",
      "Type": "String",
      "MinLength": "8",
      "MaxLength": "41",
      "AllowedPattern": "[a-zA-Z0-9]*",
      "ConstraintDescription": "must contain only alphanumeric characters."
    }
```

- **NoEcho** - This field means the password will not be seen while typing it for security reasons.
</p>
</details>

<details><summary><h4 style="display:inline">AppAMItype</h4></summary>
<p>
This field is used to determine the AMI type.  It determines how much ram and CPU is allocated to it.  
      
```javascript
"AppAMItype": {
      "Description": "Instance type for app server",
      "Type": "String",
      "Default": "t2.micro",
      "AllowedValues": [
        "t1.micro",
        "t2.nano",
        "t2.micro",
        "t2.small",
        "t2.medium",
        "t2.large"
        ]
      }
```

- **AllowedValues** - This field is always a list and will create a selectable dropdown of values that can be used in this parameter.

</p>
</details>

<details><summary><h4 style="display:inline">appKeyName</h4></summary>
<p>
This field allows us to select a keypair that will be used to ssh into the AMIs after they have been created.
      
```json
"appKeyName": {
      "Description": "EC2 KeyPair to enable SSH access to the instance",
      "Type": "AWS::EC2::KeyPair::KeyName"
    }
```

- **Type** - The type is of an AWS resource. It is looking for any keys that have been created within EC2 and creates a dropdown to show us the keys we can select.
</p>
</details>

<details><summary><h4 style="display:inline">S3BucketName</h4></summary>
<p>
This field allows us to name our S3 bucket that will be used to store our logs.
      
```json
"S3BucketName": {
      "Type": "String",
      "Description": "Name the S3 bucket to be created to store VPC flow logs.",
      "AllowedPattern": "[a-z0-9-]*"
    }
```

</p>
</details>

<details><summary><h4 style="display:inline">ExternalID</h4></summary>
<p>
This field lets us input the external ID used to connect Stealth Watch to our VPC.
      
```json
"ExternalID": {
      "Type": "String",
      "Description": "The Stealthwatch cloud Observable ID."
    }
```

</p>
</details>

<details><summary><h4 style="display:inline">AvailabilityZone1</h4></summary>
<p>
This field allows us to choose the availability zone to be used for each subnet.
      
```json
"AvailabilityZone1": {
      "Description": "The Availability Zone to use for the first subnet",
      "Type": "AWS::EC2::AvailabilityZone::Name"
    }
```

- **Type** - The type is of an AWS resource. It is looking for any availability zones that are available within EC2 and creates a dropdown to show us the zones we can select.
</p>
</details>

## Resources

The resources section is where we define the different resources we want to create within AWS. In this section we do not directly make the resources, we instead call out to another configuration file and that is the file that holds the creation information. This is what will create our nested stacks.

We will be going over the 7 resources that we are creating in this master template:

- networkSetup
- DBSetup
- SWCSetup
- appLaunchConfig
- AppAsgLb
- webLaunchConfig
- WebAsgLb

We will go over each of these resources as they are defined in the master template and then each resource will have their own section. Most of these won’t be too different from the masterTemplate, so we will only go over the if anything is different and how some of the functions are being used.

<details><summary><h4 style="display:inline">networkSetup</h4></summary>
<p>
This resource calls out to the networkSetup template and passes down parameters for the template to use. Then the nested template will create everything related to the base network.
      
```json
"networkSetup": {
      "Type": "AWS::CloudFormation::Stack",
      "Properties": {
        "TemplateURL": "https://cloudformation--json-templates.s3-ap-northeast-1.amazonaws.com/1-network-setup.json",
        "Parameters": {
          "CidrBlock": { "Ref": "CidrBlock" },
          "AvailabilityZone1": { "Ref": "AvailabilityZone1" },
          "AvailabilityZone2": { "Ref": "AvailabilityZone2" },
          "OutsideNetA": { "Ref": "OutsideNetA" },
          "OutsideNetB": { "Ref": "OutsideNetB" },
          "InsideNetA": { "Ref": "InsideNetA" },
          "InsideNetB": { "Ref": "InsideNetB" },
          "DBNetA": { "Ref": "DBNetA" }
        }
      }
    }
```

- **Type** - The type is of an AWS resource. This specific type of CloudFormation::Stack is what tells Cloudformation to look for another template and pass the parameters down to that template.
- **Properties** - It defines what will be called for the template and holds the parameters to be passed down. These properties will generally only have two sections: TemplateURL and Parameters.  
   _ **TemplateURL** - This is URL location of the template we want to call. It can be a GitHub link or anything else that is publicly accessible. But generally, we host them in AWS S3 buckets. If it is in a bucket, we do not need to make the file public.  
   _ **Parameters** - This holds the values of what will be sent to the template to be used for resource creation. This field works the same way as the parameters for the masterTemplate. \* **{"Ref":"nameOfResource"}** - For each of the parameters, we are using a reference assignment. This means we are pulling the value that was input into the parameter field called CidrBlock. It works the same way for the other parameters we create a reference for.

</p>
</details>

<details><summary><h4 style="display:inline">DBSetup</h4></summary>
<p>
This resource calls out to the DBSetup template and passes down parameters for the template to use. The nested template will then setup the database.
      
```json
"DBSetup": {
      "Type": "AWS::CloudFormation::Stack",
      "DependsOn": ["networkSetup"],
      "Properties": {
        "TemplateURL": "https://cloudformation--json-templates.s3-ap-northeast-1.amazonaws.com/2-db-setup.json",
        "Parameters": {
          "DBInstanceID": { "Ref": "DBInstanceID" },
          "DBName": { "Ref": "DBName" },
          "DBInstanceClass": { "Ref": "DBInstanceClass" },
          "DBAllocatedStorage": { "Ref": "DBAllocatedStorage" },
          "DBUsername": { "Ref": "DBUsername" },
          "DBPassword": { "Ref": "DBPassword" },
          "dbCloudformationSG": {
            "Fn::GetAtt": ["networkSetup", "Outputs.dbSG"]
          },
          "DBCloudformationSubnetA": {
            "Fn::GetAtt": ["networkSetup", "Outputs.dbSubnetA"]
          },
          "DBCloudformationSubnetB": {
            "Fn::GetAtt": ["networkSetup", "Outputs.dbSubnetB"]
          }
        }
      }
    }
```

- **DependsOn** - This field is used to make sure one resource isn't created until another is finished. In this case, the DBSetup is going to wait for the NetworkSetup to complete and then it will start. This field can take either one input that does not need to be in a list, or it can take multiple inputs if it needs to wait on multiple resources to finish up.
- **{"Fn::GetAtt":["nameOfResource","Outputs.nameOfOutput"]}** - The Fn::GetAtt is used to get attributes of a resource. For the dbCoudformationSG and subnets, we need to get a resource that was created in another template. To do that we define thigs called _Outputs_ (we will go over outputs in more detail in the nested template section). Those outputs have a name we define, and we are able to use them by using the Fn:GetAtt function. The function takes a list with two attributes. The first is the resource you want to look at, in this case it is networkSetup, and the second is the output we want. Then these attributes are passed down to the nest template being called in this resource.

</p>
</details>

<details><summary><h4 style="display:inline">SWCSetup</h4></summary>
<p>
This resource calls out to the stealthwatch template and passes down parameters for the template to use. 
      
```json
"SWCSetup": {
      "Type": "AWS::CloudFormation::Stack",
      "DependsOn": ["networkSetup"],
      "Properties": {
        "TemplateURL": "https://cloudformation--json-templates.s3-ap-northeast-1.amazonaws.com/2-swc-setup.json",
        "Parameters": {
          "VPCID": {
            "Fn::GetAtt": ["networkSetup", "Outputs.StackVPC"]
          },
          "S3BucketName": {
            "Ref": "S3BucketName"
          },
          "ExternalID": {
            "Ref": "ExternalID"
          }
        }
      }
    }
```

</p>
</details>

<details><summary><h4 style="display:inline">appLaunchConfig</h4></summary>
<p>
This resource calls out to the application launch config template and passes down parameters for the template to use. 
      
```json
"appLaunchConfig": {
      "Type": "AWS::CloudFormation::Stack",
      "DependsOn": ["DBSetup"],
      "Properties": {
        "TemplateURL": "https://cloudformation--json-templates.s3-ap-northeast-1.amazonaws.com/3-app-launch-configs.json",
        "Parameters": {
          "AppAMItype": { "Ref": "AppAMItype" },
          "AppAMI": {
            "Fn::FindInMap": ["RegionMap", { "Ref": "AWS::Region" }, "HVM"]
          },
          "appKeyName": { "Ref": "appKeyName" },
          "appCloudformationSG": {
            "Fn::GetAtt": ["networkSetup", "Outputs.appSG"]
          },
          "webCloudformationSG": {
            "Fn::GetAtt": ["networkSetup", "Outputs.webSG"]
          },
          "DB": {
            "Fn::GetAtt": ["DBSetup", "Outputs.dbEndpoint"]
          },
          "DBPassword": {
            "Ref": "DBPassword"
          },
          "DBUsername": {
            "Ref": "DBUsername"
          }
        }
      }
    }
```

- **Fn::FindInMap** - This function is used to search a map defined in the mappings section of the template. We can have multiple mappings in the mapping section but for our template we only needed one for determining which AMIs to use for each region. In this example we are searching the _RegionMap_ for the region we are in, which is defined by the AWS::Region field, and then saying to grab the virtualization type of HVM for that AMI ID.

</p>
</details>

<details><summary><h4 style="display:inline">AppAsgLb</h4></summary>
<p>
This resource calls out to the networkSetup template and passes down parameters for the template to use.
      
```json
"AppAsgLb": {
      "Type": "AWS::CloudFormation::Stack",
      "DependsOn": ["appLaunchConfig"],
      "Properties": {
        "TemplateURL": "https://cloudformation--json-templates.s3-ap-northeast-1.amazonaws.com/4-app-asg-lb.json",
        "Parameters": {
          "appLaunchConfig": {
            "Fn::GetAtt": ["appLaunchConfig", "Outputs.appLaunchConfig"]
          },
          "insideCloudformationSubnetA": {
            "Fn::GetAtt": ["networkSetup", "Outputs.insideSubnetA"]
          },
          "insideCloudformationSubnetB": {
            "Fn::GetAtt": ["networkSetup", "Outputs.insideSubnetB"]
          },
          "cloudformationVPC": {
            "Fn::GetAtt": ["networkSetup", "Outputs.StackVPC"]
          },
          "appCloudformationSG": {
            "Fn::GetAtt": ["networkSetup", "Outputs.appSG"]
          },
          "webCloudformationSG": {
            "Fn::GetAtt": ["networkSetup", "Outputs.webSG"]
          },
          "appLaunchConfigVersion": {
            "Fn::GetAtt": ["appLaunchConfig", "Outputs.appLaunchConfigVersion"]
          }
        }
      }
    }
```

</p>
</details>

<details><summary><h4 style="display:inline">webLaunchConfig</h4></summary>
<p>
This resource calls out to the web launch config template for those to be created.
      
```json
"webLaunchConfig": {
      "Type": "AWS::CloudFormation::Stack",
      "DependsOn": ["AppAsgLb"],
      "Properties": {
        "TemplateURL": "https://cloudformation--json-templates.s3-ap-northeast-1.amazonaws.com/5-web-launch-configs.json",
        "Parameters": {
          "route53DNS": {
            "Ref": "route53DNS"
          },
          "WebAMItype": { "Ref": "WebAMItype" },
          "webAMI": {
            "Fn::FindInMap": ["RegionMap", { "Ref": "AWS::Region" }, "HVM"]
          },
          "webKeyName": { "Ref": "webKeyName" },
          "appCloudformationSG": {
            "Fn::GetAtt": ["networkSetup", "Outputs.appSG"]
          },
          "webCloudformationSG": {
            "Fn::GetAtt": ["networkSetup", "Outputs.webSG"]
          },
          "appALBDNS": {
            "Fn::GetAtt": ["AppAsgLb", "Outputs.appLoadBalancerDNS"]
          }
        }
      }
    }
```

</p>
</details>

<details><summary><h4 style="display:inline">WebAsgLb</h4></summary>
<p>
This resource calls out to the web autoscaling group and load balancer template for those to be created.
      
```json
"WebAsgLb": {
      "Type": "AWS::CloudFormation::Stack",
      "DependsOn": ["webLaunchConfig"],
      "Properties": {
        "TemplateURL": "https://cloudformation--json-templates.s3-ap-northeast-1.amazonaws.com/6-web-asg-lb.json",
        "Parameters": {
          "webLaunchConfig": {
            "Fn::GetAtt": ["webLaunchConfig", "Outputs.webLaunchConfig"]
          },
          "outsideCloudformationSubnetA": {
            "Fn::GetAtt": ["networkSetup", "Outputs.outsideSubnetA"]
          },
          "outsideCloudformationSubnetB": {
            "Fn::GetAtt": ["networkSetup", "Outputs.outsideSubnetB"]
          },
          "cloudformationVPC": {
            "Fn::GetAtt": ["networkSetup", "Outputs.StackVPC"]
          },
          "appCloudformationSG": {
            "Fn::GetAtt": ["networkSetup", "Outputs.appSG"]
          },
          "webCloudformationSG": {
            "Fn::GetAtt": ["networkSetup", "Outputs.webSG"]
          },
          "webLaunchConfigVersion": {
            "Fn::GetAtt": ["webLaunchConfig", "Outputs.webLaunchConfigVersion"]
          }
        }
      }
    }
```

</p>
</details>

# Nested Templates

All of these nested templates are the same resources that are being called within the masterTemplate. It starts with the network setup, then database and stealthwatch, and so on. We will go over each of those configuration files explain what each does as we get to it. Most of the concepts will be repeated from the masterTemplate but there are some things we will need to go over when we get there.

We will go over each file in the order that they are called:

1. 1-network-setup
2. 2-db-setup
3. 2-swc-setup
4. 3-app-launch-configs
5. 4-app-asg-lb
6. 5-web-launch-configs
7. 6-web-asg-lb

<!-- ## 1-network-setup -->

<details><summary><h2 style="display:inline">1-network-setup</h2></summary>
<p>
The network setup template is the first template we need to create our architecture and is the longest file of them all.  It is the template that will be used to create the VPC, subnets, gateways, routes, and security groups. In this template, the parameters section replicates what is already in the masterTemplate.  This allows us to use the template by itself without the masterTemplate to call it. We will focus on the resources section and output section here.
    
As a note, all of these parameters should match what the masterTemplate has when calling it. Since that is how the masterTemplate parameters will be passed to this one.  If the template was used standalone then we would still have those inputs. Since it is being called by a masterTemplate, these parameters will be overwritten with what the masterTemplate sends down to it.

We will break up the file into more readable chunks for each section and resource.

### Resources

<!-- #### VPC -->
<details><summary><h4 style="display:inline">VPC</h4></summary>
<p>
This resource creates the VPC our architecture will live in. 
      
```json
"VPC": {
      "Type": "AWS::EC2::VPC",
      "Properties": {
        "CidrBlock": { "Ref": "CidrBlock" },
        "EnableDnsSupport": "true",
        "EnableDnsHostnames": "true",
        "InstanceTenancy": "default",
        "Tags": [{ "Key": "Name", "Value": { "Ref": "AWS::StackName" } }]
      }
    }
    
```

- **Type** - The type is of the AWS resource VPC. Meaning it will create a VPC with the properties we specify.
- **Properties** - The properties are the values that will be used to specify how the VPC will be created and features it will have enabled or will support.
- **CidrBlock** - We are referencing the CidrBlock parameter. It was defined in the masterTemplate but can be used here since we have defined it in this template as well.
- **EnableDnsSupport** - This is set true because we want our VPC to allow DNS to be used in our network.
- **EnableDnsHostname** - This is set to true because we want our VPC to allow hostnames to be assigned within our network.
- **InstanceTenancy** - This determines if we will use dedicated host for our instances or not. The default does not use dedicated instances. If we wanted dedicated ones, then we could change this be "dedicated"
- **Tags** - We are giving this VPC a tag of Name. This will allow us to find out VPC faster since the name always shows up in the left most column.

</p>
</details>

<!-- #### outsideSubnetA -->

<details><summary><h4 style="display:inline">outsideSubnetA</h4></summary>
<p>
This resource creates one of the outside subnets we are using in the VPC.  This process is the same for the inside subnets and DB subnets.  The only thing that changes is the reference to the Availability Zone, CidrBlock and if it should give out public IP addresses.
We have two inside, outside, and DB subnets that are created with this same process.
      
```json
"outsideSubnetA": {
      "Type": "AWS::EC2::Subnet",
      "Properties": {
        "MapPublicIpOnLaunch": true,
        "VpcId": { "Ref": "VPC" },
        "CidrBlock": { "Ref": "OutsideNetA" },
        "AvailabilityZone": { "Ref": "AvailabilityZone1" }
      }
    }
    
```

- **Type** - The type of this resource is EC2::Subnet. This means it will be using the EC2::Subnet api in cloud formation to create a subnet with the properties we specify.
- **MapPublicIpOnLaunch** - This is set to true, because we want our AMIs to get public IP addresses when they are created in the public subnet.
- **VpcId** - We are referencing the VPC, so cloud formation knows what VPC to put our subnet in.
- **CidrBlock** - The cidrblock is what ip address block we want to assign to this subnet. In this case we are assigning a /24 subnet that is being referenced from the parameters of the template. This will change for each of the subsequent subnets.
- **AvailabilityZone** - The availability

</p>
</details>

<!-- #### insideSubnetA -->

<details><summary><h4 style="display:inline">insideSubnetA</h4></summary>
<p>
This resource creates one of the inside subnets we are using in the VPC. In this one we can see that the MapPublicIP option is missing because we do not want our inside net to be publicly accessible.
      
```json
"insideSubnetA": {
      "Type": "AWS::EC2::Subnet",
      "Properties": {
        "VpcId": { "Ref": "VPC" },
        "CidrBlock": { "Ref": "InsideNetA" },
        "AvailabilityZone": { "Ref": "AvailabilityZone1" }
      }
    }
    
```

</p>
</details>

<!-- #### DBSubnetA -->

<details><summary><h4 style="display:inline">DBSubnetA</h4></summary>
<p>
This resource creates one of the Db subnets we are using in the VPC. In this one we can see that the MapPublicIP option is missing because we do not want our inside net to be publicly accessible.
      
```json
"DBSubnetA": {
      "Type": "AWS::EC2::Subnet",
      "Properties": {
        "VpcId": { "Ref": "VPC" },
        "CidrBlock": { "Ref": "DBNetA" },
        "AvailabilityZone": { "Ref": "AvailabilityZone1" }
      }
    }
    
```

</p>
</details>

<!-- #### webSG -->

<details><summary><h4 style="display:inline">webSG</h4></summary>
<p>
This resource creates a security group for the web AMIs and public subnets. It is what will allow access to certain ports from different IP addresses.
      
```json
"webSG": {
      "Type": "AWS::EC2::SecurityGroup",
      "Properties": {
        "GroupDescription": "Allow http and port 3000 to web servers",
        "VpcId": { "Ref": "VPC" },
        "SecurityGroupIngress": [
          {
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 80,
            "CidrIp": "0.0.0.0/0"
          },
          {
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 3000,
            "CidrIp": "0.0.0.0/0"
          }
        ]
      }
    }
    
```

- **Type** - The type is SecurityGroup and this will create a security group within AWS for us.
- **GroupDescription** - This is a description of what the security group does or how we want to describe it.
- **SecurityGroupIngress** - This option takes a list of parameters and each item in the list is an object. Each object contains the protocol used, from/to port that will be used to access it, and the IP range that is allowed to access that port. In our example we are allowing the whole internet to access port 80 from port 80 and port 3000 from port 80.

</p>
</details>

<!-- #### appSG -->

<details><summary><h4 style="display:inline">appSG</h4></summary>
<p>
This resource creates a security group for the internal app AMIs and subnets.   Here it depends on the outside subnets to be created and only allows access from the outside subnets.
      
```json
"appSG": {
      "Type": "AWS::EC2::SecurityGroup",
      "DependsOn": ["outsideSubnetB", "outsideSubnetA"],
      "Properties": {
        "GroupDescription": "Allow http to app server",
        "VpcId": { "Ref": "VPC" },
        "SecurityGroupIngress": [
          {
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 80,
            "CidrIp": { "Ref": "OutsideNetA" }
          },
          {
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 80,
            "CidrIp": { "Ref": "OutsideNetB" }
          },
          {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "CidrIp": { "Ref": "OutsideNetA" }
          },
          {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "CidrIp": { "Ref": "OutsideNetB" }
          }
        ]
      }
    }
    
```

</p>
</details>

<!-- #### dbSG -->

<details><summary><h4 style="display:inline">dbSG</h4></summary>
<p>
This resource creates the security group for the database subnets and database itself.  It is allowing access only from the internal network on ports 3306 that is used for MySQL. 
      
```json
"dbSG": {
      "Type": "AWS::EC2::SecurityGroup",
      "DependsOn": ["insideSubnetA", "insideSubnetB"],
      "Properties": {
        "GroupDescription": "Allow MySQL access to db",
        "VpcId": { "Ref": "VPC" },
        "SecurityGroupIngress": [
          {
            "IpProtocol": "tcp",
            "FromPort": 3306,
            "ToPort": 3306,
            "CidrIp": { "Ref": "InsideNetA" }
          },
          {
            "IpProtocol": "tcp",
            "FromPort": 3306,
            "ToPort": 3306,
            "CidrIp": { "Ref": "InsideNetB" }
          }
        ]
      }
    }
    
```

</p>
</details>

<!-- #### IG -->

<details><summary><h4 style="display:inline">IG</h4></summary>
<p>
This resource is creating an Internet Gateway for the outside network
      
```json
"IG": {
      "Type": "AWS::EC2::InternetGateway",
      "Properties": {
        "Tags": [{ "Key": "Name", "Value": "cfIG" }]
      }
    }
    
```

</p>
</details>

<!-- #### AttachGateway -->

<details><summary><h4 style="display:inline">AttachGateway</h4></summary>
<p>
This resource attaches our internet gateway to the VPC. This does not allow everything to get out of the VPC just by attaching it.  For anything to get outside, it needs to have a specific route to the internet gateway.  This is something we define later on in this configuration.
      
```json
"AttachGateway": {
      "Type": "AWS::EC2::VPCGatewayAttachment",
      "Properties": {
        "VpcId": { "Ref": "VPC" },
        "InternetGatewayId": { "Ref": "IG" }
      }
    }
    
```

- **InternetGatewayId** - This is used by the GatewayAttachment api in cloud formation to attach an internet gateway to a VPC.

</p>
</details>

<!-- #### OutsideRT -->

<details><summary><h4 style="display:inline">OutsideRT</h4></summary>
<p>
This resource creates a routing table for the VPC. We will be using this one for routes that go outside the VPC.  It is a similar setup for the inside routes.
      
```json
"OutsideRT": {
      "Type": "AWS::EC2::RouteTable",
      "Properties": {
        "VpcId": { "Ref": "VPC" }
      }
    }
    
```

</p>
</details>

<details><summary><h4 style="display:inline">myRoute</h4></summary>
<p>
This resource creates a route and puts it into a routing table we specify.
      
```json
"myRoute": {
      "Type": "AWS::EC2::Route",
      "DependsOn": "IG",
      "Properties": {
        "RouteTableId": { "Ref": "OutsideRT" },
        "DestinationCidrBlock": "0.0.0.0/0",
        "GatewayId": { "Ref": "IG" }
      }
    }
    
```
* **RouteTableId** - This ID is based on the routing table we created previously.  And it tells cloudformation we want this route to be assigned to a certain routing table.
* **DestinationCidrBlock** - This is the subnet match for the route.  In this case we are saying, if anything wants to go to the internet then this is the route to use.
* **GatewayId** - This is what will be used as the gateway to get outside the VPC. In our case, we want this route to go to the internet gateway.

</p>
</details>

<!-- #### insideRoute -->

<details><summary><h4 style="display:inline">insideRoute</h4></summary>
<p>
This resource creates an inside route for our application subnets and uses a nat gateway to allow them out to the internet for updates.
      
```json
"insideRoute": {
      "Type": "AWS::EC2::Route",
      "DependsOn": "NATGW",
      "Properties": {
        "RouteTableId": { "Ref": "InsideRT" },
        "DestinationCidrBlock": "0.0.0.0/0",
        "NatGatewayId": { "Ref": "NATGW" }
      }
    }
    
```

- **NatGatewayId** - In the outside route we specified an internet gateway to get out. But now we are using a nat gateway instead.

</p>
</details>

<!-- #### RTSubnetAssocA -->

<details><summary><h4 style="display:inline">RTSubnetAssocA</h4></summary>
<p>
This resource associates a routing table with a subnet.  In this association we are associating the outside subnet with the outside routing table.
      
```json
"RTSubnetAssocA": {
      "Type": "AWS::EC2::SubnetRouteTableAssociation",
      "Properties": {
        "SubnetId": { "Ref": "outsideSubnetA" },
        "RouteTableId": { "Ref": "OutsideRT" }
      }
    }
    
```

- **SubnetId** - This is the subnet to be associated with the routing table.
- **RouteTableId** - This is the routing table to be associated with a subnet. We can have multiple subnets on a single routing table.

</p>
</details>

<details><summary><h4 style="display:inline">NATGW</h4></summary>
<p>
This resource creates the nat gateway needed for our internal AMIs to be able to access  the internet.
      
```json
"NATGW": {
      "Type": "AWS::EC2::NatGateway",
      "DependsOn": "EIP",
      "Properties": {
        "AllocationId": { "Fn::GetAtt": ["EIP", "AllocationId"] },
        "SubnetId": { "Ref": "outsideSubnetA" }
      }
    }
    
```

- **AllocationId** - this allocation ID is used to determine what public IP the nat gateway should have.
- **SubnetId** - For a nat gateway we must put it into a public subnet so that it has internet access too.

</p>
</details>

<!-- #### EIP -->

<details><summary><h4 style="display:inline">EIP</h4></summary>
<p>
This resource creates an elastic IP address from AWS for our VPC.  This elastic IP will be used for the nat gateway.
      
```json
"EIP": {
      "DependsOn": "AttachGateway",
      "Type": "AWS::EC2::EIP",
      "Properties": {
        "Domain": "vpc"
      }
    }
    
```

</p>
</details>

### Outputs

The outputs section in this template is used to pass resources that were created in this template back to the master template so they can be used in other templates. The outputs are just referencing the values of the created resources, so we will only go over one since the format does not change, only the resource being exported does.

<details><summary><h4 style="display:inline">StackVPC</h4></summary>
<p>
This resource creates an elastic IP address from AWS for our VPC.  This elastic IP will be used for the nat gateway.
      
```json
"StackVPC": {
      "Description": "The ID of the VPC",
      "Value": { "Ref": "VPC" },
      "Export": {
        "Name": { "Fn::Sub": "${AWS::StackName}-VPCID" }
      }
    }
    
```

- **Value** - The value is the variable we are passing back to the master template. If we try access the stackVPC output, we will get whatever is set in this value parameter. In this case it is the VPC ID.
- **Export** - We are exporting a name too so it actually gets exported as something that can be found.
- **Fn:Sub** - This function allows us to substitute in an environment variable into a string so the name can be dynamic.

</p>
</details>

</p>
</details>

<details><summary><h2 style="display:inline">2-db-setup</h2></summary>
<p>
This template creates the DB and returns info about to be used in another template.  The parameters work the same as in the network setup, however, there are some that only have a type of string and no other parameters.  This is because they are parameters we need to be passed down that aren't in the masterTemplate parameters. So, they are acting as placeholders for the data to be passed down.  We use this to access outputs from other templates.

After everything has been created, we output the databases endpoint address./ The endpoint address is what is used to access the database over the network.

<details><summary><h4 style="display:inline">dbSubnetGroup</h4></summary>
<p>
This resource creates a group of two or more subnets for a database to live in.  
      
```json
"dbSubnetGroup": {
      "Type": "AWS::RDS::DBSubnetGroup",
      "Properties": {
        "DBSubnetGroupDescription": "description",
        "SubnetIds": [
          { "Ref": "DBCloudformationSubnetA" },
          { "Ref": "DBCloudformationSubnetB" }
        ],
        "Tags": [
          {
            "Key": "String",
            "Value": "String"
          }
        ]
      }
    }
    
```

- **SubnetIds** - This field takes a list of subnets to be added into the group.

</p>
</details>

<details><summary><h4 style="display:inline">DB</h4></summary>
<p>
This resource creates the actual database we will use.  
      
```json
"DB": {
      "Type": "AWS::RDS::DBInstance",
      "Properties": {
        "DBInstanceIdentifier": { "Ref": "DBInstanceID" },
        "DBName": { "Ref": "DBName" },
        "DBInstanceClass": {
          "Ref": "DBInstanceClass"
        },
        "DBSubnetGroupName": { "Ref": "dbSubnetGroup" },
        "VPCSecurityGroups": [{ "Ref": "dbCloudformationSG" }],
        "AllocatedStorage": {
          "Ref": "DBAllocatedStorage"
        },
        "Engine": "MySQL",
        "EngineVersion": "8.0.16",
        "MasterUsername": {
          "Ref": "DBUsername"
        },
        "MasterUserPassword": {
          "Ref": "DBPassword"
        }
      }
    }
  }
    
```

- **DBInstanceIdentifier** - This field is the name of the DB as it will show up in RDS.

* **DBName** - This is to name the initial database to be created when the database starts.
* **DBInstanceClass** - This tells cloud formation what vm type to use for the DB. t2.micro, m2.medium, etc...
* **DBSubnetGroupName** - This fields tell the DB which subnet group it will use.
* **VPCSecurityGroups** - The db needs a security group to allow us access to it. So, we specify which security it will use.
* **Engine** - This determines the type of database it will create. In our case we are MySQL.
* **EngineVersion** - This is the version of MySQL. More info can be found in the RDS documentation on what is supported.
* **MasterUname** - this is the administrator username for the database.
* **MasterUserPassword** - This is the password for the administrator account.

</p>
</details>

</p>
</details>

<details><summary><h2 style="display:inline">2-swc-setup</h2></summary>
<p>

<details><summary><h4 style="display:inline">S3Bucket</h4></summary>
<p>

```json
"S3Bucket": {
      "Type": "AWS::S3::Bucket",
      "DeletionPolicy": "Retain",
      "Properties": {
        "BucketName": {
          "Ref": "S3BucketName"
        }
      }
    }

```

</p>
</details>

<details><summary><h4 style="display:inline">VPCFlowLogDeliveryToS3</h4></summary>
<p>

```json
"VPCFlowLogDeliveryToS3": {
      "Type": "AWS::EC2::FlowLog",
      "Properties": {
        "ResourceId": {
          "Ref": "VPCID"
        },
        "ResourceType": "VPC",
        "TrafficType": "ALL",
        "LogDestination": {
          "Fn::GetAtt": ["S3Bucket", "Arn"]
        },
        "LogDestinationType": "s3",
        "LogFormat": "${version} ${account-id} ${interface-id} ${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${packets} ${bytes} ${start} ${end} ${action} ${log-status} ${vpc-id} ${subnet-id} ${instance-id} ${tcp-flags} ${type} ${pkt-srcaddr} ${pkt-dstaddr}",
        "MaxAggregationInterval": 60
      }
    }

```

</p>
</details>

<details><summary><h4 style="display:inline">ObservableRole</h4></summary>
<p>

```json
"ObservableRole": {
      "Type": "AWS::IAM::Role",
      "Properties": {
        "RoleName": { "Fn::Sub": "${AWS::StackName}-observble_role" },
        "AssumeRolePolicyDocument": {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Action": "sts:AssumeRole",
              "Condition": {
                "StringEquals": {
                  "sts:ExternalId": {
                    "Ref": "ExternalID"
                  }
                }
              },
              "Effect": "Allow",
              "Principal": {
                "AWS": "arn:aws:iam::############:role/userToUse"
              }
            }
          ]
        },
        "Path": "/"
      }
    }

```

- **Principal** - This is what we use to give permissions to the role as the AWS user we specify.

</p>
</details>

<details><summary><h4 style="display:inline">ObservablePolicy</h4></summary>
<p>

```json
"ObservablePolicy": {
      "Type": "AWS::IAM::Policy",
      "Properties": {
        "PolicyName": { "Fn::Sub": "${AWS::StackName}-Obsrvble_policy" },
        "PolicyDocument": {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": [
                "autoscaling:Describe*",
                "cloudtrail:LookupEvents",
                "cloudwatch:Get*",
                "cloudwatch:List*",
                "ec2:Describe*",
                "elasticache:Describe*",
                "elasticache:List*",
                "elasticloadbalancing:Describe*",
                "guardduty:Get*",
                "guardduty:List*",
                "iam:Get*",
                "iam:List*",
                "inspector:*",
                "rds:Describe*",
                "rds:List*",
                "redshift:Describe*",
                "workspaces:Describe*",
                "route53:List*",
                "logs:Describe*",
                "logs:GetLogEvents",
                "logs:FilterLogEvents",
                "logs:PutSubscriptionFilter",
                "logs:DeleteSubscriptionFilter"
              ],
              "Resource": "*"
            }
          ]
        },
        "Roles": [
          {
            "Ref": "ObservableRole"
          }
        ]
      }
    }

```

</p>
</details>

<details><summary><h4 style="display:inline">Observables3Policy</h4></summary>
<p>

```json
"Observables3Policy": {
      "Type": "AWS::IAM::Policy",
      "Properties": {
        "PolicyName": { "Fn::Sub": "${AWS::StackName}-Obsrvble_s3policy" },
        "PolicyDocument": {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": ["s3:ListBucket", "s3:GetBucketLocation"],
              "Resource": {
                "Fn::GetAtt": ["S3Bucket", "Arn"]
              }
            },
            {
              "Effect": "Allow",
              "Action": ["s3:GetObject"],
              "Resource": {
                "Fn::Join": [
                  "/",
                  [
                    {
                      "Fn::GetAtt": ["S3Bucket", "Arn"]
                    },
                    "*"
                  ]
                ]
              }
            }
          ]
        },
        "Roles": [
          {
            "Ref": "ObservableRole"
          }
        ]
      }
    }
  }

```

</p>
</details>

</p>
</details>

<details><summary><h2 style="display:inline">3-app-launch-configs</h2></summary>
<p>
The app launch configuration is the configuration that will be used when new AMIs are created.  It contains what it will do on startup and all of the information we need to create an AMI without doing the actual creation itself. We then output the application launch config to be used in other templates.

<details><summary><h4 style="display:inline">appLaunchConfig</h4></summary>
<p>
This resource creates the launch configuration we will use for the application AMIs.
      
```json
"appLaunchConfig": {
      "Type": "AWS::EC2::LaunchTemplate",
      "Properties": {
        "LaunchTemplateData": {
          "ImageId": { "Ref": "AppAMI" },
          "InstanceType": { "Ref": "AppAMItype" },
          "KeyName": { "Ref": "appKeyName" },
          "SecurityGroupIds": [{ "Ref": "appCloudformationSG" }],
          "UserData": {
            "Fn::Base64": {
              "Fn::Join": [
                "",
                [
                  "#!/bin/bash\n",
                  "sudo yum install -y epel-release yum-utils\n",
                  "sudo yum install -y http://rpms.remirepo.net/enterprise/remi-release-7.rpm\n",
                  "sudo yum-config-manager --enable remi-php73\n",
                  "sudo yum install -y php php-common php-opcache php-mcrypt php-cli php-gd php-curl php-mysqlnd\n",
                  "sudo yum install -y wget\n",
                  "sudo yum install -y unzip\n",
                  "sudo yum install -y lsof\n",
                  "sudo yum install -y httpd\n",
                  "sudo yum install -y ipset\n",
                  "sudo systemctl start httpd\n",
                  "sudo systemctl enable httpd\n",
                  "sudo setsebool -P httpd_can_network_connect 1\n",
                  "sudo wget https://wordpress.org/latest.tar.gz\n",
                  "tar -xzf latest.tar.gz\n",
                  "cd wordpress\n",
                  "sudo  wget https://safeapplabfiles.s3.amazonaws.com/wp-config.php\n",
                  "sudo sed -i -E 's/admintochange/",
                  { "Ref": "DBUsername" },
                  "/g' ./wp-config.php\n",
                  "sudo sed -i -E 's/PASSWORDTOCHANGE/",
                  { "Ref": "DBPassword" },
                  "/g' ./wp-config.php\n",
                  "sudo sed -i -E 's/dbname.region.rds.amazonaws.com/",
                  { "Ref": "DB" },
                  "/g' ./wp-config.php\n",
                  "sudo rsync -avP * /var/www/html/\n",
                  "sudo chown -R apache:apache /var/www/html/*\n",
                  "sudo systemctl restart httpd\n"
                ]
              ]
            }
          }
        }
      }
    }
  }
    
```

- **ImageId** - This field is used to tell what image will be used to create the AMI.
- **InstanceType** - This field is used to determine the resources the instance will have to use. t2.mirco, etc...
- **KeyName** - This is used to define what key will be used to ssh into the device should we need to do so.
- **SecurityGroupIds** - This is used to attach the instance to certain security groups. In this case we are attaching them to the internal application security groups.
- **UserData** - This field is used to pass script the instance will run after it has come up. For us, we are installing packages and replacing configuration file lines in it.
- **Fn::Base64** - The script needs to be encoded in base 64 to work, so we are explicitly telling it to convert it to base 64 using this function.
- **Fn::Join** - This function takes a list of two arguments. The first is the delimiter on how the second argument should be built. The second argument is a list of what you want to do. The first argument for us is an empty string, this means that after each comma in the second argument it will join the arguments with nothing in between them. We could add comma in between the quotes and it will make a large line with commas in between each item in the list.

</p>
</details>

</p>
</details>

<details><summary><h2 style="display:inline">4-app-asg-lb</h2></summary>
<p>
The app-asg-lb template is used to create the auto scaling group and load balancer for the application AMIs. After they have been created, we output the loadbalancer DNS name, and the autoscaling group.

<details><summary><h4 style="display:inline">appASG</h4></summary>
<p>
This resource creates the application auto scaling group.  This group will allow us to have the number of AMIs increase or decrease based on load.

```json
"appASG": {
      "Type": "AWS::AutoScaling::AutoScalingGroup",
      "Properties": {
        "TargetGroupARNs": [{ "Ref": "appTargetGroup" }],
        "MinSize": "1",
        "MaxSize": "2",
        "DesiredCapacity": "1",
        "LaunchTemplate": {
          "LaunchTemplateId": {
            "Ref": "appLaunchConfig"
          },
          "Version": { "Ref": "appLaunchConfigVersion" }
        },
        "VPCZoneIdentifier": [
          { "Ref": "insideCloudformationSubnetA" },
          { "Ref": "insideCloudformationSubnetB" }
        ]
      }
    }

```

- **TargetGroupARNs** - This field is used to tell what image will be used to create the AMI.
- **MinSize** - This field is to determine the minimum running amount of AMIs we want to be available.
- **MaxSize** - This will determine the maximum amount of AMIs to be available during peak load.
- **DesiredCapacity** - The desired capacity is how many should be available at any time, but can be more than the minsize and less than the maxsize.
- **LaunchTemaplate** - This is the launch template that will be used when a new AMI is created.
- **LaunchTemplateId** - This is the ID of the launch template we want to use.
- **Version** - This is the version of the launch template we want to use.
- **VPCZoneIdentifier** - These are the subnets that the autoscaling group will deploy the AMIs into.

</p>
</details>

<details><summary><h4 style="display:inline">appLoadBalancer</h4></summary>
<p>
This resource creates applicationn load balancer.  It will send requests between all of the instances in the autoscaling group.
      
```json
"appLoadBalancer": {
      "Type": "AWS::ElasticLoadBalancingV2::LoadBalancer",
      "Properties": {
        "Scheme": "internal",
        "IpAddressType": "ipv4",
        "Name": "appLoadBalancer",
        "Type": "application",
        "SecurityGroups": [{ "Ref": "appCloudformationSG" }],
        "Subnets": [
          { "Ref": "insideCloudformationSubnetA" },
          { "Ref": "insideCloudformationSubnetB" }
        ]
      }
    }
    
```

- **Scheme** - This is used to determine if the load balancer will be internet facing or not. In this case we are using an internal load balancer.
- **IpAddressType** - The type of IP to assign. We are using IPv4, not IPv6.
- **Type** - This determines if it should be an application or network load balancer.
- **SecurityGroups** - These are the security groups the laod balancer will be linked to.
- **Subnets** - These are the subnets the load balancer will live in.

</p>
</details>

<details><summary><h4 style="display:inline">appTargetGroup</h4></summary>
<p>
This resource creates a target group the auto-scaling group will use to link to. The target group will do health checks as well to determine the state of an instance.
      
```json
"appTargetGroup": {
      "Type": "AWS::ElasticLoadBalancingV2::TargetGroup",
      "Properties": {
        "HealthCheckEnabled": true,
        "HealthCheckPath": "/",
        "HealthCheckPort": "80",
        "HealthCheckProtocol": "HTTP",
        "HealthCheckTimeoutSeconds": 3,
        "HealthyThresholdCount": 3,
        "Matcher": {
          "HttpCode": "200-399"
        },
        "Name": "appTargetGroup",
        "Port": 80,
        "Protocol": "HTTP",
        "TargetType": "instance",
        "UnhealthyThresholdCount": 10,
        "VpcId": { "Ref": "cloudformationVPC" }
      }
    }
    
```

- **HealthCheckEnabled** - True because we want a health check for each instance.
- **HealthCheckPath** - The path to use for the healthcheck. We are using the root path.
- **HealthCheckPort** - The port to use for the health check.
- **HealthCheckProtocol** - Protocol to check the health of the instance.
- **HealthCheckTimeoutSeconds** - How many seconds it waits for a response before it times out.
- **HealthyThresholdCount** - How many healthy responses are needed to mark the instance as healthy.
- **Matcher** - The things to match for healthiness.
- **HttpCode** - THis is a range of codes that we are expecting if the instance is healthy. Anything outside these codes are considered unhealthy.
- **Port** - The port to sue to check for healthiness.
- **Protocol** - Which protocol is being used to check their healthiness.
- **TargetType** - This is used to say we are targeting an instance. This must be used for target groups.
- **UnhealthyThresholdCount** - How many unhealthy responses it takes to mark the target as unhealthy.
- **VpcId** - This is the id of the VPC the target group will reside in.

</p>
</details>

<details><summary><h4 style="display:inline">HTTPListenerRule</h4></summary>
<p>
This resource creates the listener rule for the load balancer listener. This is what will detrermine what to do with a request when it sees it.
      
```json
"HTTPListenerRule": {
      "Type": "AWS::ElasticLoadBalancingV2::ListenerRule",
      "Properties": {
        "Actions": [
          {
            "Type": "forward",
            "TargetGroupArn": { "Ref": "appTargetGroup" }
          }
        ],
        "Conditions": [
          {
            "Field": "source-ip",
            "SourceIpConfig": { "Values": ["0.0.0.0/0"] }
          }
        ],
        "ListenerArn": { "Ref": "HTTPlistener" },
        "Priority": 1
      }
    }
    
```

- **Actions** - This field is a list of what we want the rule to do when it matches a condition. For this action, we want it to forward the request to our app target group instances.

* **Conditions** - This field is used to determine which action will be applied when a request matches this condition. We are checking the request by source-ip and the source IP we are looking for is any IP.
* **ListenerARN** - This field used to link the rule to a listener. In this case it is out http listener.
* **Priority** This is what order the rule will be hit in. We have it set to be first.

</p>
</details>

<details><summary><h4 style="display:inline">HTTPListener</h4></summary>
<p>
This resource creates the the http listener to look for new http traffic being sent to the load balancer.
      
```json
"HTTPlistener": {
      "Type": "AWS::ElasticLoadBalancingV2::Listener",
      "Properties": {
        "DefaultActions": [
          {
            "Type": "forward",
            "TargetGroupArn": { "Ref": "appTargetGroup" }
          }
        ],
        "LoadBalancerArn": {
          "Ref": "appLoadBalancer"
        },
        "Port": 80,
        "Protocol": "HTTP"
      }
    }
  }
    
```

- **DefaultActions** - If a rule doesn't have its action, by default we will forward the requests to our app target group instances.

* **LoadBalancerArn** - This is the load balancer the listener should be linked to.
* **Port** - The port we are listening on.
* **Protocol** - The protocol we are listening for.

</p>
</details>

</p>
</details>

<details><summary><h2 style="display:inline">5-web-launch-configs</h2></summary>
<p>
The web launch config serves a similar purpose as the application launch config but with a few differences in the security group and user data script.

```json
"webLaunchConfig": {
      "Type": "AWS::EC2::LaunchTemplate",
      "Properties": {
        "LaunchTemplateData": {
          "ImageId": { "Ref": "webAMI" },
          "InstanceType": { "Ref": "WebAMItype" },
          "KeyName": { "Ref": "webKeyName" },
          "SecurityGroupIds": [{ "Ref": "webCloudformationSG" }],
          "UserData": {
            "Fn::Base64": {
              "Fn::Join": [
                "",
                [
                  "#!/bin/bash\n",
                  "sudo yum install -y epel-release\n",
                  "sudo yum install -y nginx\n",
                  "sudo yum install -y wget\n",
                  "sudo yum install -y unzip\n",
                  "sudo yum install -y lsof\n",
                  "sudo yum install -y ipset\n",
                  "cd /etc/nginx\n",
                  "sudo mv nginx.conf nginx.conf.backup\n",
                  "sudo wget https://cloudformation--json-templates.s3-ap-northeast-1.amazonaws.com/nginx.conf\n",
                  "sudo sed -i -E 's/INTERLANLB/",
                  { "Ref": "appALBDNS" },
                  "/g' nginx.conf\n",
                  "sudo systemctl restart nginx\n",
                  "sudo systemctl enable nginx\n"
                ]
              ]
            }
          }
        }
      }
    }
  }
```

</p>
</details>

<details><summary><h2 style="display:inline">6-web-asg-lb</h2></summary>
<p>

<details><summary><h4 style="display:inline">webASG</h4></summary>
<p>
This resource is creating the auto scaling group for the web servers.  It is the same as the app server group but with a different launch config and subnets.

```json
"webASG": {
      "Type": "AWS::AutoScaling::AutoScalingGroup",
      "Properties": {
        "TargetGroupARNs": [{ "Ref": "webTargetGroup" }],
        "MinSize": "1",
        "MaxSize": "2",
        "DesiredCapacity": "1",
        "LaunchTemplate": {
          "LaunchTemplateId": {
            "Ref": "webLaunchConfig"
          },
          "Version": { "Ref": "webLaunchConfigVersion" }
        },
        "VPCZoneIdentifier": [
          { "Ref": "outsideCloudformationSubnetA" },
          { "Ref": "outsideCloudformationSubnetB" }
        ]
      }
    }

```

</p>
</details>

<details><summary><h4 style="display:inline">webLoadBalancer</h4></summary>
<p>
This resource creates a load balancer for the web servers.  The difference in this one compared to the app load balancer is that this one is internet facing and in the outside subnets.

```json
"webLoadBalancer": {
      "Type": "AWS::ElasticLoadBalancingV2::LoadBalancer",
      "Properties": {
        "Scheme": "internet-facing",
        "IpAddressType": "ipv4",
        "Name": "webLoadBalancer",
        "Type": "application",
        "SecurityGroups": [{ "Ref": "webCloudformationSG" }],
        "Subnets": [
          { "Ref": "outsideCloudformationSubnetA" },
          { "Ref": "outsideCloudformationSubnetB" }
        ]
      }
    }

```

</p>
</details>

<details><summary><h4 style="display:inline">webTargetGroup</h4></summary>
<p>
This resources creates the web target group and it is similar to the appp target group.

```json
"webTargetGroup": {
      "Type": "AWS::ElasticLoadBalancingV2::TargetGroup",
      "Properties": {
        "HealthCheckEnabled": true,
        "HealthCheckPath": "/",
        "HealthCheckPort": "80",
        "HealthCheckProtocol": "HTTP",
        "HealthCheckTimeoutSeconds": 3,
        "HealthyThresholdCount": 3,
        "Matcher": {
          "HttpCode": "200-399"
        },
        "Name": "webTargetGroup",
        "Port": 80,
        "Protocol": "HTTP",
        "TargetType": "instance",
        "UnhealthyThresholdCount": 10,
        "VpcId": { "Ref": "cloudformationVPC" }
      }
    }

```

</p>
</details>

<details><summary><h4 style="display:inline">HTTPListenerRule</h4></summary>
<p>
This creates the listener rule for the web listener and is the same as the app http listener rule.

```json
"HTTPListenerRule": {
      "Type": "AWS::ElasticLoadBalancingV2::ListenerRule",
      "Properties": {
        "Actions": [
          {
            "Type": "forward",
            "TargetGroupArn": { "Ref": "webTargetGroup" }
          }
        ],
        "Conditions": [
          {
            "Field": "source-ip",
            "SourceIpConfig": { "Values": ["0.0.0.0/0"] }
          }
        ],
        "ListenerArn": { "Ref": "HTTPlistener" },
        "Priority": 1
      }
    }

```

</p>
</details>

<details><summary><h4 style="display:inline">HTTPlistener</h4></summary>
<p>
This resource creates the http listener for the web load balancer.  It is like the app http listener except it targerts the web target group.

```json
"HTTPlistener": {
      "Type": "AWS::ElasticLoadBalancingV2::Listener",
      "Properties": {
        "DefaultActions": [
          {
            "Type": "forward",
            "TargetGroupArn": { "Ref": "webTargetGroup" }
          }
        ],
        "LoadBalancerArn": {
          "Ref": "webLoadBalancer"
        },
        "Port": 80,
        "Protocol": "HTTP"
      }
    }
  }

```

</p>
</details>

</p>
</details>

# Create a resource group
resource "azurerm_resource_group" "hubRG" {
    name     = "hubRG"
    location = var.location.value
}

# Create virtual network
resource "azurerm_virtual_network" "HubVNet" {
    name                = "HubVNet"
    address_space       = ["10.10.0.0/16"]
    location            = var.location.value
    resource_group_name = azurerm_resource_group.hubRG.name
}

# Create subnet
resource "azurerm_subnet" "HubSubnetA" {
    name                 = "HubSubnetA"
    resource_group_name  = azurerm_resource_group.hubRG.name
    virtual_network_name = azurerm_virtual_network.HubVNet.name
    address_prefixes       = ["10.10.1.0/24"]
}
resource "azurerm_subnet" "HubSubnetB" {
    name                 = "HubSubnetB"
    resource_group_name  = azurerm_resource_group.hubRG.name
    virtual_network_name = azurerm_virtual_network.HubVNet.name
    address_prefixes       = ["10.10.2.0/24"]
}

# Create public IPs
resource "azurerm_public_ip" "DNGPublicIP" {
    name                         = "DNGPublicIP"
    location                     = var.location.value
    resource_group_name          = azurerm_resource_group.hubRG.name
    allocation_method            = "Dynamic"
}
resource "azurerm_public_ip" "BastionPublicIP" {
    name                         = "BastionPublicIP"
    location                     = var.location.value
    resource_group_name          = azurerm_resource_group.hubRG.name
    allocation_method            = "Dynamic"
}
resource "azurerm_public_ip" "BastionWinPublicIP" {
    name                         = "BastionWinPublicIP"
    location                     = var.location.value
    resource_group_name          = azurerm_resource_group.hubRG.name
    allocation_method            = "Dynamic"
}

# Create Network Security Group and rule
resource "azurerm_network_security_group" "HubNSG" {
    name                = "HubNSG"
    location            = var.location.value
    resource_group_name = azurerm_resource_group.hubRG.name

    security_rule {
        name                       = "SSH"
        priority                   = 1001
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "22"
        source_address_prefix      = "*"
        destination_address_prefix = "*"
    }
    security_rule {
        name                       = "HTTP"
        priority                   = 1002
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "80"
        source_address_prefix      = "*"
        destination_address_prefix = "*"
    }
    security_rule {
        name                       = "HTTPS"
        priority                   = 1003
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "443"
        source_address_prefix      = "*"
        destination_address_prefix = "*"
    }
    security_rule {
        name                       = "HTTPS-DNG"
        priority                   = 1004
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "8443"
        source_address_prefix      = "*"
        destination_address_prefix = "*"
    }
    security_rule {
        name                       = "RDP"
        priority                   = 1005
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "3389"
        source_address_prefix      = "*"
        destination_address_prefix = "*"
    }
}

# Create network interfaces
resource "azurerm_network_interface" "GitNic" {
    name                      = "GitNic"
    location                  = var.location.value
    resource_group_name       = azurerm_resource_group.hubRG.name
    internal_dns_name_label       = "safegitlab"

    ip_configuration {
        name                          = "myGitConfiguration"
        subnet_id                     = azurerm_subnet.HubSubnetA.id
        private_ip_address_allocation = "Dynamic"
    }
}
resource "azurerm_network_interface" "DNGNic" {
    name                      = "DNGNic"
    location                  = var.location.value
    resource_group_name       = azurerm_resource_group.hubRG.name

    ip_configuration {
        name                          = "myDNGConfiguration"
        subnet_id                     = azurerm_subnet.HubSubnetA.id
        private_ip_address_allocation = "Dynamic"
        public_ip_address_id          = azurerm_public_ip.DNGPublicIP.id
    }
}
resource "azurerm_network_interface" "ConnectorNic" {
    name                      = "ConnectorNic"
    location                  = var.location.value
    resource_group_name       = azurerm_resource_group.hubRG.name

    ip_configuration {
        name                          = "myConnectorConfiguration"
        subnet_id                     = azurerm_subnet.HubSubnetB.id
        private_ip_address_allocation = "Dynamic"
    }
}
resource "azurerm_network_interface" "BastionNic" {
    name                      = "BastionNic"
    location                  = var.location.value
    resource_group_name       = azurerm_resource_group.hubRG.name

    ip_configuration {
        name                          = "myBastionConfiguration"
        subnet_id                     = azurerm_subnet.HubSubnetA.id
        private_ip_address_allocation = "Dynamic"
        public_ip_address_id          = azurerm_public_ip.BastionPublicIP.id
    }
}
resource "azurerm_network_interface" "BastionWinNic" {
    name                      = "BastionWinNic"
    location                  = var.location.value
    resource_group_name       = azurerm_resource_group.hubRG.name

    ip_configuration {
        name                          = "myBastionWinConfiguration"
        subnet_id                     = azurerm_subnet.HubSubnetA.id
        private_ip_address_allocation = "Dynamic"
        public_ip_address_id          = azurerm_public_ip.BastionWinPublicIP.id
    }
}

# Connect the security group to the network interface
resource "azurerm_network_interface_security_group_association" "nsgnic1" {
    network_interface_id      = azurerm_network_interface.GitNic.id
    network_security_group_id = azurerm_network_security_group.HubNSG.id
}
resource "azurerm_network_interface_security_group_association" "nsgnic2" {
    network_interface_id      = azurerm_network_interface.DNGNic.id
    network_security_group_id = azurerm_network_security_group.HubNSG.id
}
resource "azurerm_network_interface_security_group_association" "nsgnic3" {
    network_interface_id      = azurerm_network_interface.BastionNic.id
    network_security_group_id = azurerm_network_security_group.HubNSG.id
}
resource "azurerm_network_interface_security_group_association" "nsgnic4" {
    network_interface_id      = azurerm_network_interface.BastionWinNic.id
    network_security_group_id = azurerm_network_security_group.HubNSG.id
}

# Create an SSH key
resource "tls_private_key" "vm_ssh" {
  algorithm = "RSA"
  rsa_bits = 4096
}

# Create virtual machines for Gitlab
data "template_file" "gitlab-init" {
  template = file("gitlab-user-data.sh")
  vars = {
    gitlabaddress = azurerm_network_interface.GitNic.internal_domain_name_suffix
  }
}
resource "azurerm_linux_virtual_machine" "gitlab" {
    name                  = "GitLabPrivateInstance"
    location              = var.location.value
    resource_group_name   = azurerm_resource_group.hubRG.name
    network_interface_ids = [azurerm_network_interface.GitNic.id]
    size                  = "Standard_DS1_v2"

    os_disk {
        name              = "GitOsDisk"
        caching           = "ReadWrite"
        storage_account_type = "Premium_LRS"
    }

    source_image_reference {
        publisher = "Canonical"
        offer     = "UbuntuServer"
        sku       = "18.04-LTS"
        version   = "latest"
    }

    computer_name  = "GitLabPrivateInstance"
    admin_username = "azureuser"
    disable_password_authentication = true
    custom_data = base64encode(data.template_file.gitlab-init.rendered)

    admin_ssh_key {
        username       = "azureuser"
        public_key     = tls_private_key.vm_ssh.public_key_openssh
    }
}
# Create Linux virtual machine(Duo Network Gateway)
data "template_file" "dng-init" {
  template = file("dng-user-data.sh")
}
resource "azurerm_linux_virtual_machine" "dng" {
    name                  = "DuoNetworkGateway"
    location              = var.location.value
    resource_group_name   = azurerm_resource_group.hubRG.name
    network_interface_ids = [azurerm_network_interface.DNGNic.id]
    size                  = "Standard_DS2_v2"

    os_disk {
        name              = "DNGOsDisk"
        caching           = "ReadWrite"
        storage_account_type = "Premium_LRS"
    }

    source_image_reference {
        publisher = "OpenLogic"
        offer     = "CentOS"
        sku       = "7_9-gen2"
        version   = "latest"
    }

    computer_name  = "DuoNetworkGateway"
    admin_username = "azureuser"
    disable_password_authentication = true
    custom_data = base64encode(data.template_file.dng-init.rendered)

    admin_ssh_key {
        username       = "azureuser"
        public_key     = tls_private_key.vm_ssh.public_key_openssh
    }
}

# Create Linux virtual machine(Secure Workload Connector)
resource "azurerm_linux_virtual_machine" "WorkloadConnector" {
    name                  = "SecureWorkloadConnector"
    location              = var.location.value
    resource_group_name   = azurerm_resource_group.hubRG.name
    network_interface_ids = [azurerm_network_interface.ConnectorNic.id]
    size                  = "Standard_DS2_v2"

    os_disk {
        name              = "SecureWorkloadConnectorOsDisk"
        caching           = "ReadWrite"
        storage_account_type = "Premium_LRS"
    }

    source_image_reference {
        publisher = "OpenLogic"
        offer     = "CentOS"
        sku       = "7_9-gen2"
        version   = "latest"
    }

    computer_name  = "SecureWorkloadConnector"
    admin_username = "azureuser"
    disable_password_authentication = true

    admin_ssh_key {
        username       = "azureuser"
        public_key     = tls_private_key.vm_ssh.public_key_openssh
    }
}
# Create Linux virtual machine(Bastion Host)
data "template_file" "bastion-init" {
  template = file("bastion-user-data.sh")
}
resource "azurerm_linux_virtual_machine" "bastion" {
    name                  = "Bastion"
    location              = var.location.value
    resource_group_name   = azurerm_resource_group.hubRG.name
    network_interface_ids = [azurerm_network_interface.BastionNic.id]
    size                  = "Standard_DS2_v2"

    os_disk {
        name              = "BastionOsDisk"
        caching           = "ReadWrite"
        storage_account_type = "Premium_LRS"
    }

    source_image_reference {
        publisher = "Canonical"
        offer     = "UbuntuServer"
        sku       = "18.04-LTS"
        version   = "latest"
    }

    computer_name  = "Bastion"
    admin_username = "azureuser"
    disable_password_authentication = true
    custom_data = base64encode(data.template_file.bastion-init.rendered)

    admin_ssh_key {
        username       = "azureuser"
        public_key     = tls_private_key.vm_ssh.public_key_openssh
    }
}

# Create Windows virtual machine(Bastion Host)
resource "azurerm_windows_virtual_machine" "bastionWin" {
  name                = "BastionWin"
  resource_group_name = azurerm_resource_group.hubRG.name
  location            = azurerm_resource_group.hubRG.location
  size                = "Standard_DS1_v2"
  admin_username      = var.WindowsBastionUser
  admin_password      = var.WindowsBastionPassword
  network_interface_ids = [azurerm_network_interface.BastionWinNic.id]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "MicrosoftWindowsDesktop"
    offer     = "Windows-10"
    sku       = "19h1-pro"
    version   = "latest"
  }
}

# Create VNET peering between Hub and Spoke
resource "azurerm_virtual_network_peering" "peering-12" {
  name                      = "peer1to2"
  resource_group_name       = azurerm_resource_group.hubRG.name
  virtual_network_name      = azurerm_virtual_network.HubVNet.name
  remote_virtual_network_id = azurerm_virtual_network.Spoke1VNet.id
}

resource "azurerm_virtual_network_peering" "peering-21" {
  name                      = "peer2to1"
  resource_group_name       = azurerm_resource_group.spoke1RG.name
  virtual_network_name      = azurerm_virtual_network.Spoke1VNet.name
  remote_virtual_network_id = azurerm_virtual_network.HubVNet.id
}

# Create Storage Account for SWC VPC flow logs
resource "azurerm_storage_account" "stealtchwatch-hub-ngsflowlogs" {
  name                     = "nsglogssecurecloud"
  resource_group_name      = azurerm_resource_group.hubRG.name
  location                 = azurerm_resource_group.hubRG.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    environment = "Hub"
  }
}

# Create Container Registry
resource "azurerm_container_registry" "acr" {
  name                     = var.containerregistry
  resource_group_name      = azurerm_resource_group.hubRG.name
  location                 = azurerm_resource_group.hubRG.location
  sku                      = "Basic"
  admin_enabled            = true
}

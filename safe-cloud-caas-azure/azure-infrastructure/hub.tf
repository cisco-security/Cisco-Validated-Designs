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
resource "azurerm_public_ip" "GitPublicIP" {
    name                         = "GitPublicIP"
    location                     = var.location.value
    resource_group_name          = azurerm_resource_group.hubRG.name
    allocation_method            = "Dynamic"
    domain_name_label            = "safegitlab"
}
resource "azurerm_public_ip" "BastionPublicIP" {
    name                         = "BastionPublicIP"
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
}

# Create network interfaces
resource "azurerm_network_interface" "GitNic" {
    name                      = "GitNic"
    location                  = var.location.value
    resource_group_name       = azurerm_resource_group.hubRG.name

    ip_configuration {
        name                          = "myDNGConfiguration"
        subnet_id                     = azurerm_subnet.HubSubnetA.id
        private_ip_address_allocation = "Dynamic"
        public_ip_address_id          = azurerm_public_ip.GitPublicIP.id
    }
}
resource "azurerm_network_interface" "BastionNic" {
    name                      = "BastionNic"
    location                  = var.location.value
    resource_group_name       = azurerm_resource_group.hubRG.name

    ip_configuration {
        name                          = "myDNGConfiguration"
        subnet_id                     = azurerm_subnet.HubSubnetA.id
        private_ip_address_allocation = "Dynamic"
        public_ip_address_id          = azurerm_public_ip.BastionPublicIP.id
    }
}

# Connect the security group to the network interface
resource "azurerm_network_interface_security_group_association" "nsgnic1" {
    network_interface_id      = azurerm_network_interface.GitNic.id
    network_security_group_id = azurerm_network_security_group.HubNSG.id
}
resource "azurerm_network_interface_security_group_association" "nsgnic2" {
    network_interface_id      = azurerm_network_interface.BastionNic.id
    network_security_group_id = azurerm_network_security_group.HubNSG.id
}

# Create (and display) an SSH key
resource "tls_private_key" "vm_ssh" {
  algorithm = "RSA"
  rsa_bits = 4096
}

# Create virtual machines for Gitlab
data "template_file" "gitlab-init" {
  template = file("gitlab-user-data.sh")
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

# Create virtual machine(Bastion Host)
data "template_file" "bastion-init" {
  template = file("bastion-user-data.sh")
}
resource "azurerm_linux_virtual_machine" "bastion" {
    name                  = "BastionHost"
    location              = var.location.value
    resource_group_name   = azurerm_resource_group.hubRG.name
    network_interface_ids = [azurerm_network_interface.BastionNic.id]
    size                  = "Standard_DS1_v2"

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

    computer_name  = "BastionHost"
    admin_username = "azureuser"
    disable_password_authentication = true
    custom_data = base64encode(data.template_file.bastion-init.rendered)

    admin_ssh_key {
        username       = "azureuser"
        public_key     = tls_private_key.vm_ssh.public_key_openssh
    }
}

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

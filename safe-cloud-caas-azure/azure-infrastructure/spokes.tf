resource "azurerm_resource_group" "spoke1RG" {
    name     = "Spoke1RG"
    location = var.location.value
}

# Create virtual network
resource "azurerm_virtual_network" "Spoke1VNet" {
    name                = "Spoke1VNet"
    address_space       = ["10.20.0.0/16"]
    location            = var.location.value
    resource_group_name = azurerm_resource_group.spoke1RG.name
}

# Create subnet
resource "azurerm_subnet" "Spoke1Subnet" {
    name                 = "Spoke1Subnet"
    resource_group_name  = azurerm_resource_group.spoke1RG.name
    virtual_network_name = azurerm_virtual_network.Spoke1VNet.name
    address_prefixes       = ["10.20.1.0/24"]
    enforce_private_link_endpoint_network_policies = true
}

# Create AKS cluster
resource "azurerm_kubernetes_cluster" "spoke1k8s" {
    name                = var.cluster_name
    location            = azurerm_resource_group.spoke1RG.location
    resource_group_name = azurerm_resource_group.spoke1RG.name
    dns_prefix          = var.dns_prefix
    private_cluster_enabled = true
    private_dns_zone_id = "System"

    service_principal {
        client_id     = var.client_id
        client_secret = var.client_secret
    }

    linux_profile {
        admin_username = "ubuntu"

        ssh_key {
            key_data = file(var.ssh_public_key)
        }
    }

    default_node_pool {
        name               = "nodepool"
        node_count         = var.node_count
        vm_size            = "Standard_D2_v2"
        vnet_subnet_id     = azurerm_subnet.Spoke1Subnet.id
        availability_zones = ["1", "2", "3"]
    }

    network_profile {
        load_balancer_sku = "Standard"
        network_plugin = "kubenet"
    }

    tags = {
        Environment = "Development"
    }
}

resource "azurerm_private_dns_zone_virtual_network_link" "hubspoke1link" {
  name                  = "hubspoke1link"
  resource_group_name   = "MC_${azurerm_resource_group.spoke1RG.name}_${azurerm_kubernetes_cluster.spoke1k8s.name}_${var.location.suffix}"
  private_dns_zone_name = join(".", slice(split(".", azurerm_kubernetes_cluster.spoke1k8s.private_fqdn), 1, length(split(".", azurerm_kubernetes_cluster.spoke1k8s.private_fqdn))))
  virtual_network_id    = azurerm_virtual_network.HubVNet.id
}

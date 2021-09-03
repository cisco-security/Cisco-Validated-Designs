output "client_key" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config.0.client_key
    sensitive = true
}
output "client_certificate" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config.0.client_certificate
    sensitive = true
}
output "cluster_ca_certificate" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config.0.cluster_ca_certificate
    sensitive = true
}
output "cluster_username" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config.0.username
}
output "cluster_password" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config.0.password
    sensitive = true
}
output "kube_config" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config_raw
    sensitive = true
}
output "AzureK8s" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config.0.host
}

output "vm_ssh" {
    value = tls_private_key.vm_ssh.private_key_pem
    sensitive = true
}

output "DuoNetworkGatewayHostIP" {
    value = azurerm_linux_virtual_machine.dng.public_ip_address
}

output "SecureWorkloadConnectorIP" {
    value = azurerm_linux_virtual_machine.WorkloadConnector.public_ip_address
}

output "BastionLinuxHostIP" {
    value = azurerm_linux_virtual_machine.bastion.public_ip_address
}

output "GitLabHostIP" {
    value = azurerm_linux_virtual_machine.gitlab.private_ip_address
}
output "GitLabRunnerIP" {
    value = azurerm_linux_virtual_machine.gitlab.private_ip_address
}
output "GitLabHostURL" {
    value = "http://safegitlab.${azurerm_network_interface.GitNic.internal_domain_name_suffix}"
}
output "GitLabHostFQDN" {
    value = "safegitlab.${azurerm_network_interface.GitNic.internal_domain_name_suffix}"
}

output "BastionWindowsHostIP" {
    value = azurerm_windows_virtual_machine.bastionWin.public_ip_address
}
output "BastionWindowsHostUser" {
    value = azurerm_windows_virtual_machine.bastionWin.admin_username
}
output "BastionWindowsHostPassword" {
    value = azurerm_windows_virtual_machine.bastionWin.admin_password
}

output "RegistryLogin" {
    value       = azurerm_container_registry.acr.login_server
}
output "RegistryUser" {
    value       = azurerm_container_registry.acr.admin_username 
}
output "RegistryPassword" {
    value       = azurerm_container_registry.acr.admin_password
}
output "client_key" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config.0.client_key
}

output "client_certificate" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config.0.client_certificate
}

output "cluster_ca_certificate" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config.0.cluster_ca_certificate
}

output "cluster_username" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config.0.username
}

output "cluster_password" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config.0.password
}

output "kube_config" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config_raw
}

output "host" {
    value = azurerm_kubernetes_cluster.spoke1k8s.kube_config.0.host
}

output "vm_ssh" {
    value = tls_private_key.vm_ssh.private_key_pem
    sensitive = true
}

output "BastionHostIP" {
    value = azurerm_linux_virtual_machine.bastion.public_ip_address
}

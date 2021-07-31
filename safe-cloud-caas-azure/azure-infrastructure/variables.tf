variable "client_id" {}
variable "client_secret" {}

variable "node_count" {
    default = 3
}

variable "ssh_public_key" {
    default = "~/.ssh/id_rsa.pub"
}

variable "dns_prefix" {
    default = "spoke1k8s"
}

variable cluster_name {
    default = "spoke1akscluster"
}

variable location {
    type = map(string)
    default = {
      value = "Central US"
      suffix = "centralus"
    }
}

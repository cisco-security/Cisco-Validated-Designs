#Create VPC network
resource "google_compute_network" "safe-vpc-network" {
  name                    = "safe-vpc-network"
  auto_create_subnetworks = false
}

#Create subnets in VPC network
resource "google_compute_subnetwork" "appsubnet" {
  name          = "appsubnet"
  ip_cidr_range = "10.0.2.0/24"
  region        = var.region
  network       = google_compute_network.safe-vpc-network.id
}

resource "google_compute_subnetwork" "websubnet" {
  name          = "websubnet"
  ip_cidr_range = "10.0.3.0/24"
  region        = var.region
  network       = google_compute_network.safe-vpc-network.id
}


# Create NAT Gateway for outbound connectivity
resource "google_compute_router" "router" {
  name    = "safe-router"
  region  = var.region
  network = google_compute_network.safe-vpc-network.id

  bgp {
    asn = 64514
  }
}

resource "google_compute_router_nat" "nat" {
  name                               = "safe-router-nat"
  router                             = google_compute_router.router.name
  region                             = google_compute_router.router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

#Create cloud SQL database (enable private IP and Cloud SQL Admin API prior)
resource "google_compute_global_address" "private_ip_address" {
  name          = "dbsubnet"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  address       = "10.0.1.0"
  prefix_length = 24
  network       = google_compute_network.safe-vpc-network.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.safe-vpc-network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

resource "random_id" "db_name_suffix" {
  byte_length = 4
}

resource "google_sql_database_instance" "instance" {
  name   = "safe-mysql-instance-${random_id.db_name_suffix.hex}"
  depends_on = [google_service_networking_connection.private_vpc_connection]
  region = var.region

  settings {
    tier = "db-f1-micro"
    availability_type = "REGIONAL"
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.safe-vpc-network.id
    }
    backup_configuration {
      binary_log_enabled = true
      enabled            = true
    }
  }
}

resource "google_sql_database" "wordpressdb" {
  name       = var.dbname
  instance   = google_sql_database_instance.instance.name
  depends_on = [google_sql_database_instance.instance]
}

resource "google_sql_user" "wpuser" {
  name       = var.user
  instance   = google_sql_database_instance.instance.name
  password   = var.password
  host       = "%"
  depends_on = [google_sql_database_instance.instance]
}

#Create instance template for app servers
resource "google_compute_instance_template" "appserver" {
  name        = "appserver"
  description = "This template is used to create app server instances."
  region = var.region
  depends_on = [google_sql_database_instance.instance]

  labels = {
    environment = "app-tier"
  }

  tags = ["app"]

  instance_description = "App Servers"
  machine_type         = "e2-medium"
  can_ip_forward       = false
  metadata_startup_script = templatefile("./app-startup.sh",{user=google_sql_user.wpuser.name,password=google_sql_user.wpuser.password,database=google_sql_database.wordpressdb.name,host=google_sql_database_instance.instance.private_ip_address})

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
  }
  disk {
    source_image      = "centos-cloud/centos-7"
    auto_delete       = true
    boot              = true
  }
  network_interface {
    subnetwork = google_compute_subnetwork.appsubnet.id
  }
}

#Create instance template for web servers
resource "google_compute_instance_template" "webserver" {
  name        = "webserver"
  description = "This template is used to create app server instances."
  region = var.region

  labels = {
    environment = "web-tier"
  }

  tags = ["web"]

  instance_description = "Web Servers"
  machine_type         = "e2-medium"
  can_ip_forward       = false
  metadata_startup_script = file("web-startup.sh")

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
  }
  disk {
    source_image      = "centos-cloud/centos-7"
    auto_delete       = true
    boot              = true
  }
  network_interface {
    subnetwork = google_compute_subnetwork.websubnet.id
  }
}

#Create resources for instance groups
resource "google_compute_health_check" "autohealing" {
  name                = "autohealing-health-check"
  check_interval_sec  = 5
  timeout_sec         = 5
  healthy_threshold   = 2
  unhealthy_threshold = 10 # 50 seconds

  tcp_health_check {
    port = "80"
  }
}

#Create instance group for app servers
resource "google_compute_region_instance_group_manager" "appservergroup" {
  name = "appserver-igm"

  base_instance_name = "app"
  region                     = var.region
  distribution_policy_zones  = ["us-east1-b", "us-east1-c"]

  version {
    instance_template  = google_compute_instance_template.appserver.id
  }

  target_size  = 2

  named_port {
    name = "appport"
    port = 80
  }

  auto_healing_policies {
    health_check      = google_compute_health_check.autohealing.id
    initial_delay_sec = 300
  }
}

#Create instance group for web servers
resource "google_compute_region_instance_group_manager" "webservergroup" {
  name = "webserver-igm"

  base_instance_name = "web"
  region                     = var.region
  distribution_policy_zones  = ["us-east1-b", "us-east1-c"]

  version {
    instance_template  = google_compute_instance_template.webserver.id
  }

  target_size  = 2

  named_port {
    name = "webport"
    port = 80
  }

  auto_healing_policies {
    health_check      = google_compute_health_check.autohealing.id
    initial_delay_sec = 300
  }
}

# Add firewall rules to allow SSH and HTTP
resource "google_compute_firewall" "saferules" {
  name    = "saferules"
  network = google_compute_network.safe-vpc-network.name

  allow {
    protocol = "tcp"
    ports    = ["80", "22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags = ["web","app"]
}


#Create LB for web servers
resource "google_compute_region_health_check" "webprobe" {
  region = var.region
  name   = "web-health-check"
  tcp_health_check {
    port = "80"
  }
}

resource "google_compute_region_backend_service" "web" {
  load_balancing_scheme = "EXTERNAL"
  region      = var.region
  name        = "web-service"
  protocol    = "TCP"
  timeout_sec = 10

  backend {
    group          = google_compute_region_instance_group_manager.webservergroup.instance_group
    balancing_mode = "CONNECTION"
  }

  health_checks = [google_compute_region_health_check.webprobe.id]
}

resource "google_compute_forwarding_rule" "weblb" {
  name                  = "weblb-forwarding-rule"
  region                = var.region
  load_balancing_scheme = "EXTERNAL"
  all_ports             = true
  backend_service       = google_compute_region_backend_service.web.id
  network_tier          = "STANDARD"
}

#Create LB for app servers
resource "google_compute_region_health_check" "appprobe" {
  region = var.region
  name   = "app-health-check"
  tcp_health_check {
    port = "80"
  }
}

resource "google_compute_region_backend_service" "app" {
  load_balancing_scheme = "INTERNAL"
  region      = var.region
  name        = "app-service"
  protocol    = "TCP"
  timeout_sec = 10

  backend {
    group          = google_compute_region_instance_group_manager.appservergroup.instance_group
    balancing_mode = "CONNECTION"
  }

  health_checks = [google_compute_region_health_check.appprobe.id]
}

resource "google_compute_forwarding_rule" "applb" {
  name                  = "applb-forwarding-rule"
  region                = var.region
  load_balancing_scheme = "INTERNAL"
  ports                 = ["80"]
  subnetwork            = google_compute_subnetwork.appsubnet.id
  ip_address            = "10.0.2.100"
  backend_service       = google_compute_region_backend_service.app.id
}

output "sql-dbname" {
    value = google_sql_database_instance.instance.name
    description = "The instance name for the master instance"
}

output "sqldb_private_address" {
  value       = google_sql_database_instance.instance.private_ip_address
  description = "The private IP address assigned for the master instance"
}

output "dbusername" {
  value       = google_sql_user.wpuser.name
  description = "SQL db username"
}

output "dbpassword" {
  value       = google_sql_user.wpuser.password
  description = "SQL db Password"
}

output "dbname" {
  value       = google_sql_database.wordpressdb.name
  description = "SQL database name"
}

output "frontlb" {
  value       = google_compute_forwarding_rule.weblb.ip_address
  description = "Front end load balancer"
}

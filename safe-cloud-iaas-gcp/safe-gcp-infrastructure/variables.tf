variable region {
    default = "us-east1"
}

variable user {
    default = "wpuser"
}

variable password {
    type = string
    description = "SQL db Password"
}

variable dbname {
    default = "wordpress-db"
}

// Configure the Google Cloud provider
provider "google" {
 credentials = file("gcp.json")
 project     = "gcp-gcpsafecloud-nprd-40978"
}

# Example Terraform configuration for provisioning AWS S3 bucket as a raw data source

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "raw_data_bucket" {
  bucket = "your-raw-data-bucket"
  acl    = "private"
  # Add more configurations as needed
}

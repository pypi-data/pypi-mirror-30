# Backend setup
terraform {
  backend "s3" {
    key = "sampleapp.tfstate"
  }
}

# Variable definitions
variable "region" {}

# Provider and access setup
provider "aws" {
  version = "~> 0.1"
  region = "${var.region}"
}

# Data and resources

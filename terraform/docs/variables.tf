#------------------------------------------------------------------------------
# Inputs of the documentation site's stack.
#------------------------------------------------------------------------------

variable "aws_account_id" {
  description = "The AWS account to operate on. make passes it as TF_VAR_aws_account_id, from the caller's credentials."
  type        = string
}

variable "aws_region" {
  description = "The region of the S3 bucket that holds the built site."
  type        = string
  default     = "us-east-2"
}

variable "domain_name" {
  description = "The documentation site's host name."
  type        = string
  default     = "docs.smarter-python.smarter.sh"
}

variable "hosted_zone_name" {
  description = "The Route53 hosted zone that the site's records go in."
  type        = string
  default     = "smarter.sh"
}

locals {
  bucket_name = var.domain_name

  tags = {
    Project   = "smarter-python"
    Component = "docs"
    Terraform = "true"
    Source    = "github.com/smarter-sh/smarter-python/terraform/docs"
  }
}

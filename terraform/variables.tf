variable "organization_name" {
  description = "First part of your account identifier (before the dash), e.g. ABCDEFG"
  type        = string
}

variable "account_name" {
  description = "Second part of your account identifier (after the dash), e.g. XY12345"
  type        = string
}

variable "user" {
  description = "Your Snowflake user name (the one with the RSA key of the ingestion lab)"
  type        = string
}

variable "private_key_path" {
  description = "Path to rsa_key.p8. Never commit the key itself."
  type        = string
  default     = "../../rsa_key.p8"
}

variable "bi_warehouse_size" {
  description = "Size of the warehouse used by Power BI"
  type        = string
  default     = "XSMALL"
}

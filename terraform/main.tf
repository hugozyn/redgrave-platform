# AFC Redgrave platform, declared as code.

resource "snowflake_database" "platform" {
  name    = "REDGRAVE_TF"
  comment = "Managed by Terraform - do not change by hand"
}

resource "snowflake_schema" "marts" {
  database = snowflake_database.platform.name
  name     = "MARTS"
}

module "elt_warehouse" {
  source  = "./modules/warehouse"
  name    = "REDGRAVE_TF_ELT_WH"
  size    = "XSMALL"
  comment = "Airflow, dbt and ingestion jobs"
}

module "bi_warehouse" {
  source  = "./modules/warehouse"
  name    = "REDGRAVE_TF_BI_WH"
  size    = var.bi_warehouse_size
  comment = "Power BI dashboards"
}

resource "snowflake_account_role" "analyst" {
  provider = snowflake.security
  name     = "REDGRAVE_TF_ANALYST"
  comment  = "Read-only analysts - managed by Terraform"
}

resource "snowflake_grant_privileges_to_account_role" "analyst_bi_warehouse" {
  provider          = snowflake.security
  account_role_name = snowflake_account_role.analyst.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = module.bi_warehouse.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "analyst_database" {
  provider          = snowflake.security
  account_role_name = snowflake_account_role.analyst.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.platform.name
  }
}

# Read access for the instructor (role created in the ingestion lab), so this lab can be graded
resource "snowflake_grant_privileges_to_account_role" "grader_database" {
  provider          = snowflake.security
  account_role_name = "REDGRAVE_GRADER"
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.platform.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "grader_warehouses" {
  for_each          = toset([module.elt_warehouse.name, module.bi_warehouse.name])
  provider          = snowflake.security
  account_role_name = "REDGRAVE_GRADER"
  privileges        = ["MONITOR"]
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = each.value
  }
}

resource "snowflake_grant_privileges_to_account_role" "grader_schema" {
  provider          = snowflake.security
  account_role_name = "REDGRAVE_GRADER"
  privileges        = ["USAGE"]
  on_schema {
    schema_name = snowflake_schema.marts.fully_qualified_name
  }
}

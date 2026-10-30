output "warehouses" {
  value = [module.elt_warehouse.name, module.bi_warehouse.name]
}

output "analyst_role" {
  value = snowflake_account_role.analyst.name
}

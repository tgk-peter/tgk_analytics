"""Run individual endpoint backups"""
# package imports
# local imports
from backup_funcs import list_endpoint_records


# Define from which endpoints to extract data
resources = ["customers", "price_rules", "orders", "collects", "products"]

for resource in resources:
    list_endpoint_records(resource=resource)
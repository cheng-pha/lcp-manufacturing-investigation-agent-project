import os

from azure.cosmos import CosmosClient


cosmos_client = CosmosClient(
    os.environ["COSMOS_ENDPOINT"],
    os.environ["COSMOS_KEY"]
)

database = cosmos_client.get_database_client("lcp-manufacturing")

devices_container = database.get_container_client("devices")
process_events_container = database.get_container_client("process_events")
quality_events_container = database.get_container_client("quality_events")
scrap_events_container = database.get_container_client("scrap_events")
holds_container = database.get_container_client("holds")
assembly_status_container = database.get_container_client("assembly_status")
from azure.cosmos import exceptions

from tools.database import (
    devices_container,
    process_events_container,
    holds_container,
    assembly_status_container,
)


def get_device(device_id):
    try:
        return devices_container.read_item(
            item=device_id,
            partition_key=device_id
        )
    except exceptions.CosmosResourceNotFoundError:
        return None


def get_device_history(device_id):
    query = """
    SELECT
        c.device_id,
        c.timestamp,
        c.step,
        c.status,
        c.details
    FROM c
    WHERE c.device_id = @device_id
    ORDER BY c.timestamp
    """

    parameters = [
        {
            "name": "@device_id",
            "value": device_id
        }
    ]

    results = process_events_container.query_items(
        query=query,
        parameters=parameters,
        partition_key=device_id
    )

    return list(results)


def get_assembly_status(device_id):
    query = """
    SELECT
        c.device_id,
        c.status,
        c.current_step,
        c.next_step
    FROM c
    WHERE c.device_id = @device_id
    """

    parameters = [
        {
            "name": "@device_id",
            "value": device_id
        }
    ]

    results = list(
        assembly_status_container.query_items(
            query=query,
            parameters=parameters,
            partition_key=device_id
        )
    )

    return results[0] if results else None


def get_hold_status(device_id):
    query = """
    SELECT
        c.hold_id,
        c.device_id,
        c.hold_type,
        c.required_hours,
        c.start_time,
        c.end_time,
        c.status,
        c.reason
    FROM c
    WHERE c.device_id = @device_id
    ORDER BY c.start_time
    """

    parameters = [
        {
            "name": "@device_id",
            "value": device_id
        }
    ]

    results = holds_container.query_items(
        query=query,
        parameters=parameters,
        partition_key=device_id
    )

    return list(results)


def get_devices_on_hold():
    query = """
    SELECT
        c.hold_id,
        c.device_id,
        c.hold_type,
        c.required_hours,
        c.start_time,
        c.end_time,
        c.status,
        c.reason
    FROM c
    WHERE c.status = "IN_PROGRESS"
    ORDER BY c.start_time
    """

    results = holds_container.query_items(
        query=query
    )

    return list(results)


def get_devices_by_lot(lot):
    query = """
    SELECT
        c.id,
        c.device_id,
        c.device_type,
        c.lot,
        c.current_status,
        c.current_step
    FROM c
    WHERE c.lot = @lot
    ORDER BY c.device_id
    """

    parameters = [
        {
            "name": "@lot",
            "value": lot
        }
    ]

    results = devices_container.query_items(
        query=query,
        parameters=parameters
    )

    return list(results)
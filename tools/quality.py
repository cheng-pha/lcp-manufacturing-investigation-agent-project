from tools.database import (
    quality_events_container,
    scrap_events_container,
)


def get_quality_events(device_id):
    query = """
    SELECT
        c.quality_event_id,
        c.device_id,
        c.timestamp,
        c.type,
        c.severity,
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

    results = quality_events_container.query_items(
        query=query,
        parameters=parameters,
        partition_key=device_id
    )

    return list(results)


def get_scrap_events(device_id):
    query = """
    SELECT
        c.scrap_event_id,
        c.device_id,
        c.timestamp,
        c.reason_code,
        c.reason,
        c.approved_by
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

    results = scrap_events_container.query_items(
        query=query,
        parameters=parameters,
        partition_key=device_id
    )

    return list(results)


def get_scrap_summary():
    query = """
    SELECT
        c.reason_code,
        COUNT(1) AS count
    FROM c
    GROUP BY c.reason_code
    """

    results = scrap_events_container.query_items(
        query=query
    )

    summary = {}

    for result in results:
        summary[result["reason_code"]] = result["count"]

    return summary


def get_quality_summary():
    query = """
    SELECT
        c.quality_event_id,
        c.device_id,
        c.timestamp,
        c.type,
        c.severity,
        c.status,
        c.details
    FROM c
    """

    events = quality_events_container.query_items(
        query=query
    )

    summary = {}

    for event in events:
        event_type = event["type"]

        if event_type not in summary:
            summary[event_type] = {
                "count": 0,
                "severity": {},
                "status": {},
                "events": []
            }

        summary[event_type]["count"] += 1

        severity = event["severity"]

        if severity not in summary[event_type]["severity"]:
            summary[event_type]["severity"][severity] = 0

        summary[event_type]["severity"][severity] += 1

        status = event["status"]

        if status not in summary[event_type]["status"]:
            summary[event_type]["status"][status] = 0

        summary[event_type]["status"][status] += 1

        summary[event_type]["events"].append(
            {
                "quality_event_id": event["quality_event_id"],
                "device_id": event["device_id"],
                "timestamp": event["timestamp"],
                "details": event["details"]
            }
        )

    return summary
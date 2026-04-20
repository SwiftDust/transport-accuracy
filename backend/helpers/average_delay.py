def average_delay(delays: list[dict]) -> float:
    """Calculate average delay across all stop updates in seconds.

    Args:
        delays: List of dicts with 'trip_id' and 'delay' keys

    Returns:
        Average delay in seconds
    """

    total_delay = sum(item["delay"] for item in delays)
    return total_delay / len(delays)

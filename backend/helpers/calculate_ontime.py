def amount(delays: list[dict]) -> int:
    """Count trains (unique trips) that are on time.

    Args:
        delays: List of dicts with 'trip_id' and 'delay' keys

    Returns:
        Number of unique trips that are on time (worst delay <= 60 seconds)
    """
    trip_worst_delay = {}

    for item in delays:
        trip_id = item["trip_id"]
        delay = item["delay"]

        if trip_id not in trip_worst_delay:
            trip_worst_delay[trip_id] = delay
        else:
            trip_worst_delay[trip_id] = max(trip_worst_delay[trip_id], delay)

    # count trips where worst delay is acceptable (less than 60 seconds)
    on_time_count = sum(1 for delay in trip_worst_delay.values() if delay <= 60)

    return on_time_count


def percentage(delays: list[dict]) -> float:
    """Calculate percentage of trains (unique trips) on time.

    Args:
        delays: List of dicts with 'trip_id' and 'delay' keys

    Returns:
        Percentage of unique trips with on-time arrival (worst delay <= 60 seconds)
    """
    trip_worst_delay = {}

    for item in delays:
        trip_id = item["trip_id"]
        delay = item["delay"]

        if trip_id not in trip_worst_delay:
            trip_worst_delay[trip_id] = delay
        else:
            trip_worst_delay[trip_id] = max(trip_worst_delay[trip_id], delay)

    if not trip_worst_delay:
        return 0.0

    on_time_count = sum(1 for delay in trip_worst_delay.values() if delay <= 60)

    return (on_time_count / len(trip_worst_delay)) * 100

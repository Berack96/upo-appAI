from datetime import datetime


def unified_timestamp(timestamp_ms: int | None = None, timestamp_s: int | None = None) -> str:
    """
        Transform the timestamp from milliseconds or seconds to a unified string format.
        The resulting string is a formatted string 'YYYY-MM-DD HH:MM'.
        Args:
            timestamp_ms: Timestamp in milliseconds.
            timestamp_s: Timestamp in seconds.
        Raises:
            ValueError: If neither timestamp_ms nor timestamp_s is provided.
    """
    if timestamp_ms is not None:
        timestamp = timestamp_ms // 1000
    elif timestamp_s is not None:
        timestamp = timestamp_s
    else:
        raise ValueError("Either timestamp_ms or timestamp_s must be provided")
    assert timestamp > 0, "Invalid timestamp data received"

    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
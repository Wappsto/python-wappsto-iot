"""Contain the wappsto timestamp converters."""
import datetime

from typing import Optional


def timestamp() -> str:
    """
    Return now timestamp used for Wappsto.

    The timestamp are always set to the UTC timezone.

    Returns:
        The UTC time string in ISO format.
    """
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def str_to_datetime(timestamp: str) -> datetime.datetime:
    """
    Convert the logger timestamp to a ISO-T-format w/ timezone.

    Args:
        data_string: The timestamp needed to be converted.

    Returns:
        The converted timestamp.
    """
    return datetime.datetime.strptime(
        timestamp,
        '%Y-%m-%dT%H:%M:%S.%fZ'
    )


def timestamp_converter(dt: Optional[datetime]) -> Optional[str]:
    """
    Return The default timestamp used for Wappsto.

    The timestamp are always set to the UTC timezone.

    Returns:
        The UTC time string in ISO format.
    """
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

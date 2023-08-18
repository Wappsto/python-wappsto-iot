"""Contain the wappsto timestamp converters."""
import datetime


def timestamp() -> str:
    """
    Return The default timestamp used for Wappsto.

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

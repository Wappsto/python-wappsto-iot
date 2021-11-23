

class WappstoError(Exception):
    """
    Wappsto IoT Main Exception Class.

    All Wappsto IoT exceptions are derived from this class.
    """
    pass


class ConfigNotFoundError(FileNotFoundError, WappstoError):
    """Exception used when config file(s) was not found or created."""
    pass


class ConfigFileError(ConfigNotFoundError, WappstoError):
    """Exception used when there was found an error in the Config file(s)."""
    pass

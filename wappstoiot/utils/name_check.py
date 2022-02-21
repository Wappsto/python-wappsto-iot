import string


wappsto_letters = string.digits + string.ascii_letters + " -_.~"
__wappsto_letter_set = set(wappsto_letters)


def legal_name(name: str) -> bool:
    """
    Check if the given name is legal.

    Args:
        name: the name to check.
    Return:
        True, if it is legal,
        False, if it is ilegal.
    """
    return not set(name) - __wappsto_letter_set

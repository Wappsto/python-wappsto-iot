"""Contain name checking functions."""
import string


wappsto_letters = (
    string.digits
    + string.ascii_letters
    + " !#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    + 'æøåÆØÅöäÖÄ'
)
__wappsto_letter_set = set(wappsto_letters)


def legal_name(name: str) -> bool:
    """
    Check if the given name is legal.

    Args:
        name: the name to check.

    Return:
        True, if it is legal,
        False, if it is illegal.
    """
    return not set(name) - __wappsto_letter_set


def illegal_characters(name: str) -> str:
    """
    Check if the given name is illegal.

    Args:
        name: the name to check.

    Return:
        string with all the illegal characters in the name.
    """
    return ''.join(set(name) - __wappsto_letter_set)


def remove_illegal_characters(name: str) -> str:
    """
    Remove illegal characters from given name.

    Args:
        name: the name to check.

    Return:
        string without the illegal characters in the name.
    """
    mapping_illegal = str.maketrans('', '', illegal_characters(name))
    return name.translate(mapping_illegal)

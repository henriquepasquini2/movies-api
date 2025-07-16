"""Text normalization functions"""

from functools import lru_cache
from unicodedata import normalize

import regex

_REGEX_NON_DIGIT = regex.compile(r"\D")
_REGEX_LEFT_ZERO = regex.compile(r"\b0+")


def normalized_text(
    text: str, keep_whitespaces: bool = False, remove_alphanumeric: bool = True
):
    """
    Removes accents and special characters from the given text

    Arguments:
        text (str): Text to be normalized
        keep_whitespaces (bool): When removing non-alphanumeric characters,
            keep the space where it was removed (if True) or not (if False)
        remove_alphanumeric (bool): Flag to remove alphanumeric characters (if True) or not (if False)

    Returns:
        string: Returns the normalized text
    """
    if not text:
        return text
    text = normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

    text = normalize_alphanumeric(
        text=text,
        keep_whitespaces=keep_whitespaces,
        remove_alphanumeric=remove_alphanumeric,
    )

    # Remove extra spaces
    text = regex.sub(r"\s+", " ", text).strip()

    return text


def normalize_alphanumeric(
    text: str, keep_whitespaces: bool = False, remove_alphanumeric: bool = True
):
    """
    Function to normalize alphanumeric characters

    Args:
        text (str): Text to be normalized
        keep_whitespaces (bool): When removing non-alphanumeric characters,
            keep the space where it was removed (if True) or not (if False)
        remove_alphanumeric (bool): Flag to remove alphanumeric characters (if True) or not (if False)

    Returns:
        string: Returns the normalized text
    """
    # Normalize accents to ASCII
    text = normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    rex = regex.compile(r"[^A-Za-z0-9 ]+")

    if all((remove_alphanumeric, keep_whitespaces)):
        # Remove non-alphanumeric, then collapse multiple spaces
        result = rex.sub(" ", text)
        result = regex.sub(r"\s+", " ", result).strip()
        return result
    elif remove_alphanumeric and not keep_whitespaces:
        return rex.sub("", text)
    else:
        return text

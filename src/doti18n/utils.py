from typing import (
    Any,
    List,
    Optional,
    Dict
)


def _is_plural_dict(data: Any) -> bool:
    """
    Checks if the given object resembles a dictionary for plural forms.

    This is a heuristic check. It considers an object a plural dictionary
    if it's a dictionary and contains at least one key from the CLDR plural
    categories ('zero', 'one', 'two', 'few', 'many', 'other') with a
    string value.

    :param data: The data object to check.
    :type data: Any
    :return: `True` if the object looks like a plural dictionary, `False` otherwise.
    :rtype: bool
    """

    if not isinstance(data, dict):
        return False

    plural_keys = {'zero', 'one', 'two', 'few', 'many', 'other'}
    return any(key in data and isinstance(data[key], str) for key in plural_keys)


def _get_value_by_path_single(path: List[str], data: Optional[Dict[str, Any]]) -> Any:
    """
    Helper method to retrieve a value by path only from a given dictionary.

    Used internally to check if a full path exists within a specific
    localization dictionary (current or default).

    :param path: The list of keys representing the path.
    :type path: List[str]
    :param data: The dictionary to search within. Can be None.
    :type data: Optional[Dict[str, Any]]
    :return: The value found at the path, or None if the path does not exist
             or data is not a dictionary.
    :rtype: Any
    """

    if data is None or not isinstance(data, dict):
        return None

    value = data
    for key in path:
        if isinstance(value, dict) and key in value:
            value = value.get(key)
        else:
            return None  # Path does not exist in this dictionary
    return value


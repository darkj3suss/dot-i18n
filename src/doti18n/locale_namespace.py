from typing import (
    List,
    Any
)


class LocaleNamespace:
    """
    Represents a nested namespace of localizations accessible via dot notation.

    This class is used by LocaleTranslator to provide access
    to nested YAML structures like `messages.status.online`.
    """

    def __init__(self, path: List[str], translator: 'LocaleTranslator'):
        """
        Initializes a LocaleNamespace.

        :param path: The list of keys representing the path to this namespace.
        :type path: List[str]
        :param translator: The LocaleTranslator instance this namespace belongs to.
        :type translator: LocaleTranslator
        """

        self._path = path
        self._translator = translator

    def __getattr__(self, name: str) -> Any:
        """
        Handles attribute access (e.g., `messages.greeting`).

        This method constructs the new path and delegates the value resolution
        to the associated LocaleTranslator.

        :param name: The attribute name (the next key in the path).
        :type name: str
        :return: The resolved value, which could be a string, another
                 LocaleNamespace, a plural handler callable, or None.
        :rtype: Any
        """

        new_path = self._path + [name]
        return self._translator._resolve_value_by_path(new_path)

    def __call__(self, *args, **kwargs) -> Any:
        """
        Handles attempts to call the object (e.g., `messages.greeting()`).

        This raises a TypeError because LocaleNamespace objects represent
        namespaces or simple values, not callable functions (unless it's
        a plural handler returned by `__getattr__` for a plural dict).

        :raises TypeError: If the LocaleNamespace object is called.
        """

        full_key_path = '.'.join(self._path) if self._path else "root"
        raise TypeError(
            f"'{type(self).__name__}' object at path '{full_key_path}' is not callable. "
            f"It represents a localization namespace or a simple value. "
            f"Access nested keys using dot notation (e.g., .title) or format plural keys (e.g., .apples(5))."
        )

    def __str__(self) -> str:
        path_str = '.'.join(self._path) if self._path else "root"
        return f"<LocaleNamespace at path '{path_str}' for '{self._translator.locale_code}'>"

    def __repr__(self) -> str:
        return self.__str__()

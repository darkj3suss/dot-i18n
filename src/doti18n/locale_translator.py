from typing import (
    List,
    Any,
    Optional,
    Dict,
    Tuple
)
import logging
from .locale_namespace import LocaleNamespace
from .utils import _is_plural_dict

logger = logging.getLogger(__name__)
try:
    from babel import Locale
except ImportError:
    logger.warning("Babel is not installed. Library working can be unstable")

    class Locale:
        """Dummy Locale class"""
        def __init__(self, *args, **kwargs):
            pass

        def plural_form(self, *args, **kwargs):
            return "other"


class LocaleTranslator:
    """
    Represents a set of localizations for a specific locale and provides methods
    to access them and handle plural forms.
    Can be used independently, without `LocaleData`.
    """

    def __init__(
            self,
            locale_code: str,
            current_locale_data: Optional[Dict[str, Any]],
            default_locale_data: Optional[Dict[str, Any]],
            default_locale_code: str
    ):
        """
        Initializes a LocaleTranslator.

        :param locale_code: The code of the locale this translator handles (e.g., 'en', 'ru').
        :type locale_code: str
        :param current_locale_data: The raw localization data (as a dictionary) for the current locale.
                                    Can be None if the locale file was not found or invalid.
        :type current_locale_data: Optional[Dict[str, Any]]
        :param default_locale_data: The raw localization data (as a dictionary) for the default locale.
                                    Can be None if the default locale file was not found or invalid.
        :type default_locale_data: Optional[Dict[str, Any]]
        :param default_locale_code: The code of the default locale.
        :type default_locale_code: str
        """
        self.locale_code = locale_code
        self._current_locale_data = current_locale_data if isinstance(current_locale_data, dict) else {}
        self._default_locale_data = default_locale_data if isinstance(default_locale_data, dict) else {}
        self._default_locale_code = default_locale_code

    def _get_value_by_path(self, path: List[str]) -> Tuple[Any, Optional[str]]:
        """
        Retrieves the value at the given path, checking the current locale first,
        then the default locale.

        Returns the value found and the locale code where it was found.
        Returns (None, None) if the path does not exist in either locale.

        :param path: The list of keys representing the path (e.g., ['messages', 'greeting']).
        :type path: List[str]
        :return: A tuple containing the value (Any) and the locale code (Optional[str])
                 where the value was found. Returns (None, None) if not found.
        :rtype: Tuple[Any, Optional[str]]
        """

        # TODO: rework
        current_data = self._current_locale_data
        default_data = self._default_locale_data

        current_step_data = current_data
        default_step_data = default_data
        found_locale_code_at_step = None

        for i, key in enumerate(path):
            value_at_step = None

            if isinstance(current_step_data, dict) and key in current_step_data:
                value_at_step = current_step_data.get(key)
                current_step_data = value_at_step
                if found_locale_code_at_step is None or found_locale_code_at_step == self.locale_code:
                    found_locale_code_at_step = self.locale_code
            else:
                current_step_data = None

            if value_at_step is None:
                if isinstance(default_step_data, dict) and key in default_step_data:
                    value_at_step = default_step_data.get(key)
                    default_step_data = value_at_step
                    found_locale_code_at_step = self._default_locale_code
                else:
                    default_step_data = None

            if value_at_step is None:
                return None, None

            if i < len(path) - 1 and not isinstance(value_at_step, dict):
                return None, None

        final_value = value_at_step
        found_in_current_path = self._get_value_by_path_single(path, self._current_locale_data) is not None

        if found_in_current_path:
            return final_value, self.locale_code
        elif final_value is not None:
            return final_value, self._default_locale_code
        else:
            return None, None

    def _get_plural_form_key(self, count: int, locale_code: Optional[str]) -> str:
        """
        Determines the plural form key based on a number and locale code,
        using CLDR rules via the babel library.

        :param count: The number for which to determine the plural form.
        :type count: int
        :param locale_code: The locale code to use for plural rules. If None,
                            uses the translator's current locale code.
        :type locale_code: Optional[str]
        :return: The plural form key (e.g., 'one', 'few', 'many', 'other').
                 Returns 'other' as a fallback in case of errors.
        :rtype: str
        """
        target_locale_code = locale_code if locale_code else self.locale_code
        try:
            # Babel's Locale expects underscores for territory (e.g., en_US)
            locale_obj = Locale(target_locale_code.replace('-', '_'))
            plural_rule_func = locale_obj.plural_form
            return plural_rule_func(abs(count))
        except Exception as e:
            logger.warning(
                f"Babel failed to get plural rule function or category for count {count}"
                f" and locale '{target_locale_code}': {e}. Falling back to 'other'.",
                exc_info=True
            )
            return 'other'

    def _get_plural_template(
            self,
            path: List[str],
            count: int,
            current_plural_dict: Dict[str, Any],
            current_plural_locale_code: Optional[str]
    ) -> Optional[str]:
        """
        Retrieves the plural template string based on the count and locale rules.
        Searches first in the provided plural dictionary, then in the default locale's
        corresponding plural dictionary.

        :param path: The full path to the plural dictionary.
        :type path: List[str]
        :param count: The number used to determine the plural form.
        :type count: int
        :param current_plural_dict: The plural dictionary found in the current locale
                                    (or the first locale where it was found).
        :type current_plural_dict: Dict[str, Any]
        :param current_plural_locale_code: The locale code where `current_plural_dict` was found.
                                           Used for getting the plural form key.
        :type current_plural_locale_code: Optional[str]
        :return: The template string for the determined plural form, or the 'other' form,
                 or None if no suitable template is found in either locale.
        :rtype: Optional[str]
        """

        form_key = self._get_plural_form_key(count, current_plural_locale_code)
        template = current_plural_dict.get(form_key)
        if template is None:
            template = current_plural_dict.get('other')

        if template is None:
            default_plural_dict = self._get_value_by_path_single(path, self._default_locale_data)

            if (
                    default_plural_dict is not None
                    and isinstance(default_plural_dict, dict)
                    and _is_plural_dict(default_plural_dict)
            ):
                template = default_plural_dict.get(form_key)
                if template is None:
                    template = default_plural_dict.get('other')

        return template if isinstance(template, str) else None

    def _handle_resolved_value(self, value: Any, path: List[str], found_locale_code: Optional[str]) -> Any:
        """
        Helper method to process the value obtained from `_get_value_by_path`.

        Returns a string, a plural handler callable, a LocaleNamespace,
        or the value itself (e.g., number, list, bool).

        :param value: The value retrieved by `_get_value_by_path`.
        :type value: Any
        :param path: The full path used to retrieve the value.
        :type path: List[str]
        :param found_locale_code: The locale code where the value was found.
        :type found_locale_code: Optional[str]
        :return: The processed value or handler.
        :rtype: Any
        :raises ValueError: If formatting a plural string fails.
        :raises AttributeError: If a template for a plural form is not a string.
        """
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            if _is_plural_dict(value):
                def plural_handler(count: int, **kwargs) -> str:
                    """
                    Handler function returned for plural localization keys.

                    Formats the appropriate plural template based on the count.

                    :param count: The number used to determine the plural form.
                    :type count: int
                    :param kwargs: Additional keyword arguments to format into the template.
                    :type kwargs: Any
                    :return: The formatted localization string.
                    :rtype: str
                    :raises AttributeError: If a template cannot be found for the given count and key.
                    :raises ValueError: If formatting the template fails (e.g., missing placeholder).
                    """
                    template = self._get_plural_template(
                        path,
                        count,
                        value,
                        found_locale_code
                    )

                    if template is None:
                        full_key_path_str = '.'.join(path)
                        form_key = self._get_plural_form_key(count, found_locale_code)
                        raise AttributeError(
                            f"Failed to find plural template for key '{full_key_path_str}' "
                            f"(form '{form_key}', count {count}) in locale '{found_locale_code or self.locale_code}' "
                            f"or default '{self._default_locale_code}'."
                        )

                    # TODO: add more values, and, maybe, rework func
                    format_args = {'count': abs(count)}
                    format_args.update(kwargs)
                    try:
                        return template.format(**format_args)
                    except KeyError as e:
                        full_key_path_str = '.'.join(path)
                        form_key = self._get_plural_form_key(count, found_locale_code)
                        raise ValueError(
                            f"Formatting error for plural key '{full_key_path_str}' (form '{form_key}'): "
                            f"Missing placeholder {e} in template '{template}'"
                        )
                    except AttributeError:
                        full_key_path_str = '.'.join(path)
                        form_key = self._get_plural_form_key(count, found_locale_code)
                        raise ValueError(
                            f"Error: Template for key '{full_key_path_str}' form '{form_key}' is not a string."
                        )

                return plural_handler
            else:
                # Return a LocaleNamespace for nested dictionaries that are not plural dicts
                return LocaleNamespace(path, self)
        else:
            # Return other data types (numbers, lists, booleans, etc.) as is.
            if value is None:
                if found_locale_code is None:
                    full_key_path = '.'.join(path)
                    logger.warning(
                        f"Locale '{self.locale_code}': key '{full_key_path}' resolved to None "
                        f"in translations (including default '{self._default_locale_code}')."
                    )
                # Return None even if a warning is logged
                return value

    def _resolve_value_by_path(self, path: List[str]) -> Any:
        """
        Internal method to retrieve and process a value given its full path.

        Used by both LocaleNamespace and the Translator itself.

        :param path: The list of keys representing the full path.
        :type path: List[str]
        :return: The resolved value or handler.
        :rtype: Any
        """

        value, found_locale_code = self._get_value_by_path(path)
        if value is None and found_locale_code is None:
            full_key_path = '.'.join(path)
            logger.warning(
                f"Locale '{self.locale_code}': key '{full_key_path}' not found "
                f"in translations (including default '{self._default_locale_code}')."
            )
            return None

        return self._handle_resolved_value(value, path, found_locale_code)

    def __getattr__(self, name: str) -> Any:
        """
        Handles attribute access for the top level (e.g., `data['en'].messages`).

        Delegates the resolution to `_resolve_value_by_path`.

        :param name: The attribute name (the first key in the path).
        :type name: str
        :return: The resolved value, which could be a string, LocaleNamespace,
                 plural handler, or None.
        :rtype: Any
        """

        return self._resolve_value_by_path([name])

    def __call__(self, *args, **kwargs) -> Any:
        """
        Handles attempts to call the LocaleTranslator object directly.

        This is not supported, access keys via dot notation.

        :raises TypeError: If the LocaleTranslator object is called.
        """

        raise TypeError(
            f"'{type(self).__name__}' object is not callable directly. "
            "Access keys using dot notation (e.g., .greeting, .apples(5))."
        )

    def __str__(self) -> str:
        return f"<LocaleTranslator for '{self.locale_code}'>"

    def __repr__(self) -> str:
        return f"<LocaleTranslator object for '{self.locale_code}'>"

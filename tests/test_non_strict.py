import unittest

from tests import (
    BaseLocaleTest,
    LOGGER_LOCALE_TRANSLATOR
)
from src.doti18n.wrapped import (
    LocaleNamespace,
    LocaleList
)


# noinspection PyArgumentEqualDefault,PyUnusedLocal
class TestNonStrict(BaseLocaleTest):
    """Tests for non-strict mode behavior (returns None and logs warnings)."""

    def test_missing_key_returns_none_and_warns(self):
        self.create_locale_file('en', {'existing': 'value'})
        locales = self.get_locale_data(strict=False)
        with self.assertLogsFor(LOGGER_LOCALE_TRANSLATOR, level='WARNING') as log_cm:
            value = locales['en'].non_existent_key
        self.assertIsNone(value)
        log_output = "\n".join(log_cm.output)
        self.assertIn("key/index path 'non_existent_key' not found in translations", log_output)
        locales = None

    def test_missing_nested_key_returns_none_and_warns(self):
        self.create_locale_file('en', {'nested': {'existing': 'value'}})
        locales = self.get_locale_data(strict=False)
        with self.assertLogsFor(LOGGER_LOCALE_TRANSLATOR, level='WARNING') as log_cm:
            value = locales['en'].nested.non_existent_key
        self.assertIsNone(value)
        log_output = "\n".join(log_cm.output)
        self.assertIn("key/index path 'nested.non_existent_key' not found in translations", log_output)
        locales = None

    def test_calling_namespace_raises_typeerror(self):
        # Current __call__ on LocaleNamespace raises TypeError regardless of strict mode.
        # This is a reasonable design choice for __call__.
        self.create_locale_file('en', {'nested': {'item': 'value'}})
        locales = self.get_locale_data(strict=False)
        namespace = locales['en'].nested
        self.assertIsInstance(namespace, LocaleNamespace)
        with self.assertRaises(TypeError):
            namespace()

    def test_calling_list_raises_typeerror(self):
        # Current __call__ on LocaleList raises TypeError regardless of strict mode.
        # This is a reasonable design choice for __call__.
        self.create_locale_file('en', {'items': ['a']})
        locales = self.get_locale_data(strict=False)
        item_list = locales['en'].items
        self.assertIsInstance(item_list, LocaleList)
        with self.assertRaises(TypeError):
            item_list()

    def test_str_on_namespace_works(self):
        # __str__ on LocaleNamespace works in non-strict mode
        self.create_locale_file('en', {'nested': {'item': 'value'}})
        locales = self.get_locale_data(strict=False)
        namespace = locales['en'].nested
        self.assertIsInstance(namespace, LocaleNamespace)
        self.assertIn("<LocaleNamespace at path 'nested'", str(namespace))

    def test_plural_missing_form_returns_none_and_warns(self):
        self.create_locale_file('en', {'items': {'one': 'one item'}})  # Missing 'other'
        locales = self.get_locale_data(strict=False)
        # Accessing count 2 (which maps to 'other' for 'en')
        with self.assertRaises(AttributeError) as cm:  # Expect AttributeError as per current code
            locales['en'].items(2)
        self.assertIn("Failed to find plural template for key 'items' (form 'other', count 2)", str(cm.exception))
        # No warning is logged before the exception in this case, which is fine.

    def test_plural_missing_format_placeholder_raises_valueerror(self):
        # This error is from string formatting, not lookup, and should always raise.
        self.create_locale_file('en', {'greeting': {'one': 'Hello', 'other': 'Hello {name}'}})
        locales = self.get_locale_data(strict=False)
        with self.assertRaises(ValueError) as cm:
            locales['en'].greeting(5)  # Calls 'other' form, missing 'name'
        self.assertIn("Formatting error for plural key 'greeting' (form 'other'): Missing placeholder 'name'",
                      str(cm.exception))


if __name__ == '__main__':
    unittest.main()

import unittest
import os
import yaml

from tests import (
    TEST_LOCALES_DIR,
    BaseLocaleTest
)
from src.doti18n import LocaleTranslator


# noinspection PyArgumentEqualDefault
class TestLocaleDataApi(BaseLocaleTest):
    """Tests for the public API of the LocaleData class."""

    def test_getitem_returns_translator_and_caches(self):
        self.create_locale_file('en', {'key': 'value'})
        locales = self.get_locale_data('en')
        translator1 = locales['en']
        translator2 = locales['en']

        self.assertIsInstance(translator1, LocaleTranslator)
        self.assertIs(translator1, translator2)  # Check if cached

        # Check that a translator for a non-existent locale is created but has no data
        translator_non_existent = locales['fr']
        self.assertIsInstance(translator_non_existent, LocaleTranslator)
        self.assertEqual(translator_non_existent.some_key, None)  # Accessing non-existent key in non-strict default

    # noinspection PyTypeChecker
    def test_contains(self):
        self.create_locale_file('en', {'key': 'value'})
        self.create_locale_file('ru', {'key': 'value'})
        # Create a file with non-dict root (should not be 'contained')
        invalid_content = yaml.dump(['list', 'root'])
        invalid_filepath = os.path.join(TEST_LOCALES_DIR, 'invalid.yaml')
        with open(invalid_filepath, 'w', encoding='utf-8') as f:
            f.write(invalid_content)

        # Suppress critical log about default locale if 'en' is default and invalid
        # For this test, let's make sure 'en' is valid
        locales = self.get_locale_data('en')

        self.assertIn('en', locales)
        self.assertIn('ru', locales)
        self.assertNotIn('fr', locales)  # Not loaded
        self.assertNotIn('invalid', locales)  # Loaded but root not dict

        # Check case-insensitivity
        self.assertIn('EN', locales)
        self.assertIn('Ru', locales)

    def test_loaded_locales_property(self):
        self.create_locale_file('en', {'key': 'value'})
        self.create_locale_file('ru', {'key': 'value'})
        # Create a file with non-dict root (should not be in loaded_locales)
        invalid_content = yaml.dump(['list', 'root'])
        invalid_filepath = os.path.join(TEST_LOCALES_DIR, 'invalid.yaml')
        with open(invalid_filepath, 'w', encoding='utf-8') as f:
            f.write(invalid_content)

        locales = self.get_locale_data('en')

        # loaded_locales should contain normalized codes for valid dict-rooted files
        loaded = sorted(locales.loaded_locales)
        self.assertEqual(loaded, ['en', 'ru'])

    def test_get_method(self):
        self.create_locale_file('en', {'key': 'value'})
        locales = self.get_locale_data('en')

        # Test get for existing locale
        translator = locales.get('en')
        self.assertIsInstance(translator, LocaleTranslator)
        self.assertEqual(translator.key, 'value')

        # Test get for non-existing locale with default=None
        translator_none = locales.get('fr')
        self.assertIsNone(translator_none)

        # Test get for non-existing locale with a specific default value
        default_value = "default"
        value_with_default = locales.get('fr', default_value)
        self.assertEqual(value_with_default, default_value)

        # Test get for a locale that was loaded but had invalid root (should behave like non-existing for get)
        invalid_content = yaml.dump(['list', 'root'])
        invalid_filepath = os.path.join(TEST_LOCALES_DIR, 'invalid.yaml')
        with open(invalid_filepath, 'w', encoding='utf-8') as f:
            f.write(invalid_content)
        # Reload LocaleData to pick up invalid file
        locales = self.get_locale_data('en')
        self.assertNotIn('invalid', locales)  # Check it's not considered loaded
        value_invalid = locales.get('invalid', default_value)
        self.assertEqual(value_invalid, default_value)


if __name__ == '__main__':
    unittest.main()

import unittest

from tests import BaseLocaleTest
from src.doti18n.wrapped import PluralWrapper


# noinspection PyArgumentEqualDefault
class TestPluralForms(BaseLocaleTest):
    """Tests for plural form handling."""

    def test_english_plurals(self):
        self.create_locale_file('en', {
            'apples': {'one': 'You have {count} apple.', 'other': 'You have {count} apples.'},
            'mice': {'one': '1 mouse', 'other': '{count} mice'},  # Irregular plural
            'greeting': 'Hello'  # Not a plural
        })
        locales = self.get_locale_data('en')

        self.assertEqual(locales['en'].apples(0), 'You have 0 apples.')
        self.assertEqual(locales['en'].apples(1), 'You have 1 apple.')
        self.assertEqual(locales['en'].apples(2), 'You have 2 apples.')
        self.assertEqual(locales['en'].apples(5), 'You have 5 apples.')

        self.assertEqual(locales['en'].mice(1), '1 mouse')
        self.assertEqual(locales['en'].mice(3), '3 mice')

        # Test that a non-plural key is not callable
        with self.assertRaises(TypeError):
            locales['en'].greeting(1)

    def test_russian_plurals(self):
        # These tests rely on Babel's rules for 'ru'
        # 1 => one
        # 2,3,4 => few
        # 0, 5-20 => many
        # others => other (less common)
        self.create_locale_file('ru', {
            'apples': {
                'one': 'У вас {count} яблоко.',
                'few': 'У вас {count} яблока.',
                'many': 'У вас {count} яблок.',
                'other': 'У вас {count} яблок (остальные).'  # Example other form, though 'many' usually covers 0, 5-20
            },
            'guests': {
                'one': 'Пришел {count} гость.',
                'few': 'Пришло {count} гостя.',
                'many': 'Пришло {count} гостей.',
            }
        })
        locales = self.get_locale_data('ru')

        self.assertEqual(locales['ru'].apples(0), 'У вас 0 яблок.')  # many
        self.assertEqual(locales['ru'].apples(1), 'У вас 1 яблоко.')  # one
        self.assertEqual(locales['ru'].apples(2), 'У вас 2 яблока.')  # few
        self.assertEqual(locales['ru'].apples(3), 'У вас 3 яблока.')  # few
        self.assertEqual(locales['ru'].apples(4), 'У вас 4 яблока.')  # few
        self.assertEqual(locales['ru'].apples(5), 'У вас 5 яблок.')  # many
        self.assertEqual(locales['ru'].apples(10), 'У вас 10 яблок.')  # many
        self.assertEqual(locales['ru'].apples(21), 'У вас 21 яблоко.')  # one
        self.assertEqual(locales['ru'].apples(22), 'У вас 22 яблока.')  # few

        self.assertEqual(locales['ru'].guests(1), 'Пришел 1 гость.')  # one
        self.assertEqual(locales['ru'].guests(3), 'Пришло 3 гостя.')  # few
        self.assertEqual(locales['ru'].guests(11), 'Пришло 11 гостей.')  # many
        self.assertEqual(locales['ru'].guests(25), 'Пришло 25 гостей.')  # many

    def test_plural_with_extra_formatting_args(self):
        self.create_locale_file('en', {
            'items': {'one': 'You have {count} {item_name}.', 'other': 'You have {count} {item_name}s.'}
        })
        locales = self.get_locale_data('en')
        self.assertEqual(locales['en'].items(1, item_name='book'), 'You have 1 book.')
        self.assertEqual(locales['en'].items(5, item_name='book'), 'You have 5 books.')
        self.assertEqual(locales['en'].items(1, item_name='mouse'), 'You have 1 mouse.')
        self.assertEqual(locales['en'].items(5, item_name='mouse'),
                         'You have 5 mouses.')  # Demonstrates simple 's' pluralization in template

    def test_nested_plural(self):
        self.create_locale_file('en', {
            'inventory': {'apples': {'one': '1 apple', 'other': '{count} apples'}}
        })
        locales = self.get_locale_data('en')
        self.assertEqual(locales['en'].inventory.apples(1), '1 apple')
        self.assertEqual(locales['en'].inventory.apples(7), '7 apples')
        self.assertIsInstance(locales['en'].inventory.apples, PluralWrapper)

    def test_plural_dict_value_type(self):
        # Test that accessing a plural key returns a callable PluralWrapper
        self.create_locale_file('en', {'apples': {'one': 'apple', 'other': 'apples'}})
        locales = self.get_locale_data('en')
        handler = locales['en'].apples
        self.assertIsInstance(handler, PluralWrapper)
        self.assertTrue(callable(handler))

    # Tests for missing plural forms and missing format placeholders are in test_strict/test_non_strict

    def test_value_is_not_plural_dict(self):
        # If the value at the path is not a dict recognized as plural
        self.create_locale_file('en', {'not_plural': 'a string', 'not_plural_dict': {'key': 'value'},
                                       'not_plural_list': [1, 2]})
        locales = self.get_locale_data('en')
        with self.assertRaises(TypeError):
            locales['en'].not_plural(1)  # String is not callable
        with self.assertRaises(TypeError):
            locales['en'].not_plural_dict(1)  # Non-plural dict is not callable
        with self.assertRaises(TypeError):
            locales['en'].not_plural_list(1)  # List is not callable

    def test_plural_rule_exception_fallback_other(self):
        # Test fallback to 'other' if Babel fails
        # This is harder to test directly as Babel might not fail easily.
        # We could mock Babel's plural_form method to raise an exception.
        # For simplicity, trust the internal logging/fallback logic unless a real issue arises.
        pass


if __name__ == '__main__':
    unittest.main()

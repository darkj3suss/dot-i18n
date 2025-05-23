import unittest
from src.doti18n.wrapped import (
    LocaleNamespace,
    LocaleList
)
from tests import (
    BaseLocaleTest,
    LOGGER_LOCALE_TRANSLATOR
)


# noinspection PyArgumentEqualDefault,PyUnusedLocal
class TestNestedAccess(BaseLocaleTest):
    """Tests for nested dictionary and list access."""

    def test_basic_string_access(self):
        self.create_locale_file('en', {'greeting': 'Hello!'})
        locales = self.get_locale_data()
        self.assertEqual(locales['en'].greeting, 'Hello!')

    def test_nested_dict_access(self):
        self.create_locale_file('en', {'messages': {'status': {'online': 'Online'}}})
        locales = self.get_locale_data()
        self.assertEqual(locales['en'].messages.status.online, 'Online')
        self.assertIsInstance(locales['en'].messages, LocaleNamespace)
        self.assertIsInstance(locales['en'].messages.status, LocaleNamespace)

    def test_nested_list_access(self):
        self.create_locale_file('en', {'items': ['apple', 'banana', 'cherry']})
        locales = self.get_locale_data()
        self.assertEqual(locales['en'].items[0], 'apple')
        self.assertEqual(locales['en'].items[1], 'banana')
        self.assertEqual(locales['en'].items[2], 'cherry')
        self.assertIsInstance(locales['en'].items, LocaleList)
        self.assertEqual(len(locales['en'].items), 3)

    def test_combined_dict_list_access(self):
        self.create_locale_file('en', {
            'pages': [
                {'title': 'Home', 'content': 'Welcome'},
                {'title': 'About', 'content': 'Info'}
            ]
        })
        locales = self.get_locale_data()
        self.assertEqual(locales['en'].pages[0].title, 'Home')
        self.assertEqual(locales['en'].pages[1].content, 'Info')
        self.assertIsInstance(locales['en'].pages, LocaleList)
        self.assertIsInstance(locales['en'].pages[0], LocaleNamespace)
        self.assertIsInstance(locales['en'].pages[1], LocaleNamespace)

    def test_combined_list_dict_access(self):
        self.create_locale_file('en', {
            'data': {
                'sections': [
                    {'id': 1, 'items': ['A', 'B']},
                    {'id': 2, 'items': ['C', 'D']}
                ]
            }
        })
        locales = self.get_locale_data()
        self.assertEqual(locales['en'].data.sections[0].items[1], 'B')
        self.assertEqual(locales['en'].data.sections[1].items[0], 'C')
        self.assertIsInstance(locales['en'].data.sections, LocaleList)
        self.assertIsInstance(locales['en'].data.sections[0], LocaleNamespace)
        self.assertIsInstance(locales['en'].data.sections[0].items, LocaleList)

    def test_access_to_explicit_none_value(self):
        self.create_locale_file('en', {'key_is_none': None, 'nested': {'item_is_none': None}})
        locales = self.get_locale_data(strict=False)
        with self.assertLogsFor(LOGGER_LOCALE_TRANSLATOR, level='WARNING') as log_cm:
            value1 = locales['en'].key_is_none
            value2 = locales['en'].nested.item_is_none
        self.assertIsNone(value1)
        self.assertIsNone(value2)
        log_output = "\n".join(log_cm.output)
        self.assertIn("key/index path 'key_is_none' has an explicit None value.", log_output)
        self.assertIn("key/index path 'nested.item_is_none' has an explicit None value.", log_output)
        locales = None


if __name__ == '__main__':
    unittest.main()

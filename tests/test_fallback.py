import unittest

from tests import BaseLocaleTest


# noinspection PyArgumentEqualDefault
class TestFallback(BaseLocaleTest):
    """Tests for the default locale fallback mechanism."""

    def test_key_only_in_default(self):
        self.create_locale_file('en', {'only_in_en': 'English only'})
        self.create_locale_file('ru', {'ru_key': 'Russian key'})
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].only_in_en, 'English only')  # Should fallback

    def test_key_only_in_current(self):
        self.create_locale_file('en', {'en_key': 'English key'})
        self.create_locale_file('ru', {'only_in_ru': 'Russian only'})
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].only_in_ru, 'Russian only')  # Should not fallback

    def test_key_in_both_prefers_current(self):
        self.create_locale_file('en', {'key_in_both': 'English version'})
        self.create_locale_file('ru', {'key_in_both': 'Russian version'})
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].key_in_both, 'Russian version')  # Should prefer ru

    def test_nested_key_only_in_default(self):
        self.create_locale_file('en', {'nested': {'item': 'English item'}})
        self.create_locale_file('ru', {'other_root': 'value'})
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].nested.item, 'English item')  # Should fallback

    def test_nested_key_in_both_prefers_current(self):
        self.create_locale_file('en', {'nested': {'item': 'English item', 'shared': 'English'}})
        self.create_locale_file('ru', {'nested': {'item': 'Russian item', 'ru_only': 'Russian'}})
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].nested.item, 'Russian item')  # Prefer ru.nested.item
        self.assertEqual(locales['ru'].nested.shared, 'English')  # Fallback for nested.shared

    def test_list_item_fallback(self):
        # List structure exists in current, but item content falls back
        self.create_locale_file('en',
                                {'items': [{'name': 'Apple', 'desc': 'Sweet'}, {'name': 'Banana', 'desc': 'Yellow'}]})
        self.create_locale_file('ru', {'items': [{'name': 'Яблоко'}, {'name': 'Банан'}]})  # Missing 'desc' in ru items
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].items[0].name, 'Яблоко')  # Prefer ru.items[0].name
        self.assertEqual(locales['ru'].items[0].desc, 'Sweet')  # Fallback for ru.items[0].desc
        self.assertEqual(locales['ru'].items[1].name, 'Банан')  # Prefer ru.items[1].name
        self.assertEqual(locales['ru'].items[1].desc, 'Yellow')  # Fallback for ru.items[1].desc

    def test_list_fallback_entire_list(self):
        # Entire list exists only in default
        self.create_locale_file('en', {'list_only_in_en': ['a', 'b']})
        self.create_locale_file('ru', {'ru_item': 'stuff'})
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].list_only_in_en[0], 'a')  # Fallback for entire list and its item
        self.assertEqual(locales['ru'].list_only_in_en[1], 'b')

    def test_fallback_chain_dict_list_dict(self):
        self.create_locale_file('en', {
            'section': {
                'items': [
                    {'detail': 'English detail 1'},
                    {'detail': 'English detail 2'}
                ]
            }
        })
        self.create_locale_file('ru', {
            'section': {
                'items': [
                    {'id': 1},  # 'detail' missing in ru item
                    {'id': 2}
                ]
            }
        })
        locales = self.get_locale_data(default_locale='en')
        self.assertEqual(locales['ru'].section.items[0].id, 1)  # Prefer ru path segment
        self.assertEqual(locales['ru'].section.items[0].detail, 'English detail 1')  # Fallback for nested key

    def test_plural_fallback_template(self):
        # Plural structure exists in current (ru), but a specific form template falls back to default (en)
        self.create_locale_file('en', {
            'apples': {
                'one': '1 English apple',
                'other': '{count} English apples'
            }
        })
        self.create_locale_file('ru', {
            'apples': {
                'one': '1 Русское яблоко',
                # 'few', 'many', 'other' forms are missing in ru
            }
        })
        locales = self.get_locale_data(default_locale='en')
        # These tests rely on Babel's plural rules for 'ru'
        # Assuming ru rules are 1='one', 2-4='few', 5-20='many', other='other'
        self.assertEqual(locales['ru'].apples(1), '1 Русское яблоко')  # Use ru 'one'
        self.assertEqual(locales['ru'].apples(3), '3 English apples')  # Fallback to en 'other'
        self.assertEqual(locales['ru'].apples(10), '10 English apples')  # Fallback to en 'other'
        self.assertEqual(locales['ru'].apples(25), '25 English apples')  # Fallback to en 'other'


if __name__ == '__main__':
    unittest.main()

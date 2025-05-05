import os
import logging
from src.doti18n import LocaleData
from src.doti18n.wrapped import PluralWrapper

# Configure basic logging to see warnings (for fallback/missing in non-strict)
# Set level to INFO or WARNING to see the warnings from the library
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
# You can also set the level specifically for the library's loggers if needed
# logging.getLogger('src.doti18n.locale_translator').setLevel(logging.WARNING)

# Assuming this script is in the 'examples' directory relative to the project root
# and locales are in 'examples/locales'
examples_dir = os.path.dirname(__file__)
locales_dir = os.path.join(examples_dir, 'locales')

print(f"Loading locales from: {locales_dir}")

# Initialize LocaleData in non-strict mode (default)
# Default locale is 'en'

# noinspection PyArgumentEqualDefault
data = LocaleData(locales_dir, default_locale='en', strict=False)

print("\n--- Basic Access (Dictionaries and Lists) ---")

en_translator = data["en"]
ru_translator = data["ru"]

# Access simple strings via dot notation (dictionaries)
print("EN Greeting:", en_translator.messages.greeting)
print("RU Greeting:", ru_translator.messages.greeting)
print("EN Status Online:", en_translator.messages.status.online)

# Access elements in a list via index notation
print("\n--- List Access ---")
print("EN Page 1 Title:", en_translator.pages[0].title)
print("EN Page 2 Content:", en_translator.pages[1].content)

# Access nested lists and dictionaries via combined notation
print("\n--- Combined Access ---")
print("EN Section 1 Item 1 Text:", en_translator.sections[0].items[0].text)
print("EN Section 2 Item 1 Value:", en_translator.sections[1].items[0].value)

# Handling placeholders in simple strings
# You get the string template first
welcome_template = en_translator.messages.welcome_user
# Then use standard Python string formatting methods
print("EN Welcome User:", welcome_template.format(username="Alice"))

print("\n--- Wrapper Objects ---")
# When you access a dictionary or a list, you get a wrapper object, not the raw Python object
pages_list = en_translator.pages
print(f"Type of 'pages': {type(pages_list)}")
print(f"Is 'pages' a Python list instance? {isinstance(pages_list, list)}")
print(f"Representation of 'pages': {pages_list!r}")  # Use !r to show the representation defined in __repr__

page_item = en_translator.pages[0]  # Accessing an item in the list (which is a dict)
print(f"Type of 'pages[0]': {type(page_item)}")
print(f"Is 'pages[0]' a Python dict instance? {isinstance(page_item, dict)}")
print(f"Representation of 'pages[0]': {page_item!r}")

# Accessing a plural key returns a specific wrapper object
apple_handler = en_translator.items.apple
print(f"Type of 'items.apple': {type(apple_handler)}")
print(f"Is 'items.apple' a PluralHandlerWrapper? {isinstance(apple_handler, PluralWrapper)}")
print(f"Representation of 'items.apple': {apple_handler!r}")

# Note: You cannot call LocaleNamespace or LocaleList objects directly like functions
# try:
#     print("Attempting to call a LocaleList object:")
#     pages_list()
# except TypeError as e:
#     print(f"Caught expected error when calling LocaleList: {e}")

# try:
#     print("\nAttempting to call a LocaleNamespace object:")
#     page_item()
# except TypeError as e:
#     print(f"Caught expected error when calling LocaleNamespace: {e}")

# Note: In strict mode, calling str() on LocaleList or PluralHandlerWrapper raises TypeError.
# In non-strict mode, str() returns the __str__ representation defined on the wrapper.
# print("\nString representation of pages_list:", str(pages_list))
# print("String representation of apple_handler:", str(apple_handler))


print("\n--- Pluralization ---")

# Requires Babel installed (pip install dot-i18n[pluralization])
try:
    # Accessing the plural key returns a callable object
    apple_plural_en = en_translator.items.apple

    # Call it, passing the count
    print("EN Apple (1):", apple_plural_en(1))
    print("EN Apple (5):", apple_plural_en(5))
    print("EN Apple (0):", apple_plural_en(0))  # 'other' form is often used for 0

    # Example with additional formatting arguments (if template supports it)
    # If your YAML had: fancy_apple: { one: "1 {color} apple", other: "{count} {color} apples" }
    # You could call:
    # print("EN Fancy Apple (1, red):", en_translator.items.fancy_apple(1, color="red"))
    # print("EN Fancy Apple (5, blue):", en_translator.items.fancy_apple(5, color="blue"))

    apple_plural_ru = ru_translator.items.apple
    print("\nRU Apple (1):", apple_plural_ru(1))  # one
    print("RU Apple (3):", apple_plural_ru(3))  # few
    print("RU Apple (5):", apple_plural_ru(5))  # many
    print("RU Apple (21):", apple_plural_ru(21))  # one
    print("RU Apple (100):", apple_plural_ru(100))  # many

except AttributeError:
    print("\nSkipping pluralization examples: 'items.apple' key not found.")
except TypeError as e:
    print(f"\nSkipping pluralization examples due to TypeError: {e}")
    print("Make sure Babel is installed (`pip install dot-i18n[pluralization]`) and plural keys are correct.")
except Exception as e:
    print(f"\nAn unexpected error occurred during pluralization examples: {e}")

print("\n--- Fallback to Default Locale ('en') ---")
# When a key/path is missing in the current locale (ru), it falls back to the default (en).

# ru.yml does not contain messages.status.offline
print("RU Status Offline (fallback):", ru_translator.messages.status.offline)

# ru.yml does not contain messages.welcome_user
print("RU Welcome User (fallback):", ru_translator.messages.welcome_user)

# ru.yml does not contain 'content' key in pages[0] item
print("RU Page 1 Content (fallback):", ru_translator.pages[0].content)

# ru.yml is missing the entire 'sections' root key
print("RU Section 1 Item 1 Text (fallback):", ru_translator.sections[0].items[0].text)

print("\n--- Handling Missing Paths (Non-Strict) ---")
# In non-strict mode, accessing a path that doesn't exist returns None and logs a warning.

# Example 1: Accessing a root key that doesn't exist
# This call returns None and logs a warning
print("Accessing a missing root key 'non_existent_root_key'...")
value = ru_translator.non_existent_root_key
print(f"Value: {value}")  # Output: None

# Example 2: Accessing an out-of-bounds index in a list
print("\nAccessing out-of-bounds index en_translator.pages[10]...")
en_translator = data["en"]  # Ensure en_translator is used for its pages list
value = en_translator.pages[10]  # List 'pages' only has 2 items (indices 0 and 1)
print(f"Value: {value}")  # Output: None, logs WARNING

# Example 3: Attempting to access a nested path where an intermediate segment is missing.
# Accessing ru_translator.this will return None (and log a warning).
# Attempting to access .key on that returned None results in a standard Python AttributeError.
print("\nAttempting to access a nested missing path 'this.key.does.not.exist'...")
print("(Note: accessing 'this' directly will return None and log a warning)")
first_level_value = ru_translator.this  # This returns None, logs WARNING
print(f"Value of ru_translator.this: {first_level_value}")

# The next step in the chain (first_level_value.key) will raise AttributeError
# if first_level_value is None. The library's path resolution stops when it hits None.
# The error here is a standard Python error, not a localization library error message about the full path.
# try:
#     final_value = ru_translator.this.key.does.not.exist
# except AttributeError as e:
#     print(f"Caught expected standard Python error when chaining access on None: {e}")


print("\n--- Handling Explicit Null Values ---")
# If a key exists but its value is explicitly 'null' in YAML, it returns None.
# In non-strict mode, this also logs a warning (different from "not found").

# Assuming 'en.yaml' has 'explicit_null_key: null' and 'nested.another_null: null'
print("Accessing explicit_null_key (value is null in YAML)...")
value = en_translator.explicit_null_key
print(f"Value: {value}")  # Output: None, logs WARNING "has an explicit None value"

print("\nAccessing nested.another_null (value is null in YAML)...")
value = en_translator.nested.another_null
print(f"Value: {value}")  # Output: None, logs WARNING "has an explicit None value"

# This demonstrates that an explicit null value is different from a path not found at all.

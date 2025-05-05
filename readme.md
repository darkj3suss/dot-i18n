# doti18n [![PyPI version](https://badge.fury.io/py/dot-i18n.svg)](https://pypi.org/project/dot-i18n/) [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/darkj3suss/dot-i18n/blob/main/LICENSE)

Simple and intuitive Python library for loading localizations from YAML files and accessing them easily using dot notation, with powerful support for plural forms and nested data structures.

## Description

doti18n provides a convenient way to manage your application's localization strings. By loading data from standard YAML files, the library allows you to access nested translations using a simple **dot syntax (`messages.status.online`) for dictionary keys** and **index syntax (`items[0]`) for list elements**. You can combine these for intuitive navigation through complex nested structures (`pages[0].title`).

Special attention is given to pluralization support using the [Babel](https://pypi.org/project/babel/) library, which is critical for correct localization across different languages. An automatic fallback mechanism to the default locale's value is also implemented if a key or path is missing in the requested locale.

The library offers both a forgiving non-strict mode (returning a special wrapper and logging warnings) and a strict mode (raising exceptions) for handling missing paths.

It's designed for ease of use and performance (data is loaded once during initialization and translator objects are cached).

## Features

*   Loading localization data from YAML files.
*   Intuitive access to nested data structures (dictionaries and lists) using **dot notation (`.`) for dictionary keys and index notation (`[]`) for list elements**.
*   Support for **combined access paths** (`data.list[0].nested_key`).
*   **Strict mode** (`strict=True`) to raise exceptions (`AttributeError`, `IndexError`, `TypeError`) on missing paths or incorrect usage.
*   **Non-strict mode** (default) to return a special `NoneWrapper` object and log a warning on missing paths.
*   Pluralization support for count-dependent strings (requires `Babel`).
*   Automatic fallback to the default locale if a key/path is missing in the current locale.
*   Caching of loaded data and translator objects for efficient access.
*   Handles explicit `null` values in YAML, distinguishing them from missing paths.

## Installation

doti18n is available on [PyPI](https://pypi.org/project/dot-i18n/).

Install the basic version (without pluralization support):

```bash
pip install dot-i18n
```

For pluralization support (recommended), install with the optional `pluralization` dependency:

```bash
pip install dot-i18n[pluralization]
```

**Note:** Pluralization support is implemented using the [Babel](https://pypi.org/project/babel/) library. If you install dot-i18n without the `[pluralization]` optional dependency, pluralization functionality will be limited or unavailable, and the library will log a warning about the missing Babel dependency.

## Usage

### 1. Localization File Structure

Place your YAML localization files in a dedicated directory. The filename (without the extension) should correspond to the locale code (e.g., `en.yaml`, `ru.yml`, `fr.yaml`).

Example `locales/` directory structure:

```
locales/
├── en.yaml
└── ru.yml
```

Example `en.yaml` content (now including lists):

```yaml
# en.yaml
messages:
  greeting: Hello!
  status:
    online: You are online.
    offline: You are offline.
  welcome_user: "Welcome, {username}!" # Example string with a placeholder

items:
  apple:
    one: "You have {count} apple."
    other: "You have {count} apples." # Example for plural forms

settings:
  language: English
  theme: dark

pages: # Example using a list of dictionaries
  - title: Home
    path: /
    content: Welcome to the homepage!
  - title: About Us
    path: /about
    content: Learn more about our company.

sections: # Example with nested lists and dictionaries
  - id: 1
    name: Introduction
    items:
      - text: First item in section 1
        value: 10
      - text: Second item in section 1
        value: 20
  - id: 2
    name: Conclusion
    items:
      - text: Only item in section 2
        value: 30
```

Example `ru.yml` content:

```yaml
# ru.yml
messages:
  greeting: Привет!
  status:
    online: Вы онлайн.
    # Key 'offline' is missing, will fall back to en.yaml
  # Key 'welcome_user' is missing, will fall back to en.yaml

items:
  apple:
    one: "У вас {count} яблоко."
    few: "У вас {count} яблока."
    many: "У вас {count} яблок."
    other: "У вас {count} яблока." # Example for plural forms
    # 'zero' and 'two' forms can be added if needed

pages: # List structure exists, but maybe some keys/items are missing or different
  - title: Главная
    path: /
    # 'content' key is missing, will fall back to en.yaml
  - title: О нас
    # Entire second item might have missing keys or be missing itself (fallback applies per-path-segment)

sections: # This entire section is missing in ru.yml, will fall back to en.yaml
  # ...
```

### 2. Initialize `LocaleData`

Create an instance of the `LocaleData` class, specifying the path to your localization files directory and the default locale code. You can also enable `strict` mode here.

```python
from doti18n import LocaleData
import os

# Assuming your localization files are in a 'locales' subdirectory relative to the script
locales_dir = os.path.join(os.path.dirname(__file__), 'locales') # Use your actual path

# Initialize in non-strict mode (default)
data_non_strict = LocaleData(locales_dir, default_locale='en', strict=False)

# Initialize in strict mode
data_strict = LocaleData(locales_dir, default_locale='en', strict=True)
```

### 3. Accessing Translations (Dot and Index Notation)

Access translator objects using `data['locale_code']`. Then, use dot notation for dictionary keys and index notation for list elements.

```python
# Using the non-strict data instance
en_translator = data_non_strict["en"]
ru_translator = data_non_strict["ru"]

# Access simple strings via dot notation (dictionaries)
print(en_translator.messages.greeting)           # Output: Hello!
print(ru_translator.messages.greeting)           # Output: Привет!

print(en_translator.messages.status.online)      # Output: You are online.

# Access elements in a list via index notation
print(en_translator.pages[0].title)              # Output: Home
print(en_translator.pages[1].content)            # Output: Learn more about our company.

# Access nested lists and dictionaries via combined notation
print(en_translator.sections[0].items[0].text)   # Output: First item in section 1
print(en_translator.sections[1].items[0].value)  # Output: 30

# Handling placeholders in simple strings
welcome_template = en_translator.messages.welcome_user # Get the string template
print(welcome_template.format(username="Alice")) # Use standard string formatting

# Accessing list/dict wrappers themselves
# Accessing data.pages returns a LocaleList wrapper object
pages_list = en_translator.pages
print(isinstance(pages_list, list)) # Output: False
# print(pages_list) # Prints a representation like <LocaleList object at path 'pages'>
# Accessing data.pages[0] returns a LocaleNamespace wrapper object
page_item = en_translator.pages[0]
# print(page_item) # Prints a representation like <LocaleNamespace object at path 'pages.0'>
print(isinstance(page_item, dict)) # Output: False

# Note: You cannot call LocaleNamespace or LocaleList objects directly like functions
# page_item() # Raises TypeError
# pages_list() # Raises TypeError

# You also cannot implicitly convert LocaleList or PluralHandlerWrapper to string in strict mode
# print("List:", pages_list) # In strict mode, this will raise TypeError. In non-strict, prints the repr.
# It's best to access specific string values within them: print(pages_list[0].title)
```

### 4. Working with Pluralization

If a key's value is a dictionary with plural form keys (`one`, `few`, `many`, `other`, etc.), accessing this key via dot notation will return a **callable object (`PluralHandlerWrapper`)**. Call this object, passing the number (`count`) as the first argument. You can also pass additional keyword arguments for string formatting if your template strings include corresponding placeholders (e.g., `{item_name}`).

**Requires Babel (`pip install dot-i18n[pluralization]`)**

```python
# Using the non-strict data instance
en_translator = data_non_strict['en']
ru_translator = data_non_strict['ru']

# The 'apple' key returns a callable PluralHandlerWrapper object
apple_plural_en = en_translator.items.apple

# Call it, passing the count
print(apple_plural_en(1)) # Output: You have 1 apple.
print(apple_plural_en(5)) # Output: You have 5 apples.
print(apple_plural_en(0)) # Output: You have 0 apples.

# Pass additional formatting arguments
# If your template is "You have {count} {item_name}."
# You can call:
# print(apple_plural_en(1, item_name="red apple")) # Output: You have 1 red apple.
# print(apple_plural_en(5, item_name="red apple")) # Output: You have 5 red apples.
# The absolute value of 'count' passed to the handler is available as `{count}` in the template format.

# Get the translator for the Russian locale
apple_plural_ru = ru_translator.items.apple

print(apple_plural_ru(1))   # Output: У вас 1 яблоко.
print(apple_plural_ru(3))   # Output: У вас 3 яблока.
print(apple_plural_ru(5))   # Output: У вас 5 яблок.
print(apple_plural_ru(21))  # Output: У вас 21 яблоко.
print(apple_plural_ru(100)) # Output: У вас 100 яблок.
```

### 5. Fallback to Default Locale

If a key or path segment is missing in the requested locale's data, the library will attempt to find it in the default locale specified during `LocaleData` initialization. This applies recursively.

```python
# Using the non-strict data instance
ru_translator = data_non_strict['ru'] # Default locale is 'en'

# ru.yml does not contain the key messages.status.offline
print(ru_translator.messages.status.offline) # Output: You are offline. (value from en.yaml)

# ru.yml does not contain the key messages.welcome_user
print(ru_translator.messages.welcome_user) # Output: Welcome, {username}! (value from en.yaml)

# ru.yml does not contain the 'content' key in the first 'pages' item
print(ru_translator.pages[0].content) # Output: Welcome to the homepage! (value from en.yaml)

# ru.yml is missing the entire 'sections' root key
print(ru_translator.sections[0].items[0].text) # Output: First item in section 1 (value from en.yaml)
```

### 6. Handling Missing Paths (Non-Strict vs. Strict)

The behavior when a full path is not found in either the current locale or the default locale depends on the `strict` setting.

**Default Behavior (Non-Strict: `strict=False`)**

Accessing a missing key/path returns a special object `NoneWrapper` instead of raising an exception, and logs a warning. This `NoneWrapper` object allows for continued chained access (e.g., `locales['en'].nonexistent.key`) without immediate errors, with each subsequent access also returning a `NoneWrapper`.

The `NoneWrapper` object is designed to behave like `None` in common scenarios, but it is **not** the built-in `None` object.

*   It is equal to `None` when using the equality operator `==`: `locales['en'].missing_key == None` will return `True`.
*   It behaves as a "falsy" value in a boolean context: `if not locales['en'].missing_key:` will evaluate to `True`.

**Important Note: Avoid `is None` in Non-Strict Mode**

Because the library returns a `NoneWrapper` object (not the actual `None`), using the `is` operator to check for the absence of a key will **not** work as expected.

```python
# WARNING: INCORRECT WAY TO CHECK FOR ABSENCE IN NON-STRICT MODE
value = locales['en'].potentially_missing_key

# This check will be False if value is NoneWrapper, breaking your logic
if value is None:
    print("Key not found (this line will NOT be printed for NoneWrapper)")
```

**Correct Ways to Check for Absence in Non-Strict Mode:**

Please use the equality operator `==` or the boolean "falsiness" check:

```python
# CORRECT WAYS TO CHECK FOR ABSENCE IN NON-STRICT MODE
value = locales['en'].potentially_missing_key

# Using equality comparison (recommended for explicit checks)
if value == None:
    print("Key not found")

# Using boolean falsiness check (suitable if you want to treat absence as an empty value)
if not value:
    print("Key not found")

# Alternatively, check that the value is NOT an instance of NoneWrapper (less common)
if not isinstance(value, NoneWrapper):
     # You have a string, number, list, dict (non-plural), or actual None (very rare)
     print("Received a real value or structure")
else:
     print("Key not found, it's a NoneWrapper")

```

Here's the example demonstrating `NoneWrapper` return and logging:

```python
# Using the non-strict data instance
ru_translator = data_non_strict['ru'] # Default is 'en'
en_translator = data_non_strict['en']

# The path 'this.key.does.not.exist' does not exist in either en.yaml or ru.yml
value = ru_translator.this.key.does.not.exist
# Using print(value) will show the NoneWrapper representation, not just "None"
print(f"Returned value: {value}") # Example output: Returned value: NoneWrapper('ru': this.key.does.not.exist)

# When accessing, a warning will also appear in the logs from LocaleTranslator
# WARNING:src.doti18n.locale_translator:Locale 'ru': key/index path 'this' not found in translations...
# (Subsequent accesses like .key, .does, etc., will cause further warnings from NoneWrapper)


# Accessing an out-of-bounds index in a list
value = en_translator.pages[10] # List 'pages' only has 2 items (indices 0 and 1)
print(f"Returned value: {value}") # Example output: Returned value: NoneWrapper('en': pages.10)

# A warning will also appear in the logs from LocaleTranslator
# WARNING:src.doti18n.locale_translator:Locale 'en': Index out of bounds or path invalid for path 'pages.10'...
```
**Important:** To see these warnings, ensure your application has configured logging. A basic setup is `logging.basicConfig(level=logging.INFO)`.

**Strict Mode (`strict=True`)**

Initialize `LocaleData` with `strict=True`. Accessing a missing key/path will raise an exception.

```python
# Using the strict data instance
ru_translator_strict = data_strict['ru'] # Default is 'en'

# Accessing a missing key/path raises AttributeError
try:
    _ = ru_translator_strict.this.key.does.not.exist
except AttributeError as e:
    print(f"Strict mode error: {e}")
    # Example Output: Strict mode error: Locale 'ru': Strict mode error: Key/index path 'this.key.does.not.exist' not found in translations...

# Accessing an out-of-bounds index raises IndexError
try:
    _ = ru_translator_strict.pages[10] # List 'pages' in ru has only 2 items (indices 0 and 1)
except IndexError as e:
    print(f"Strict mode error: {e}")
    # Example Output: Strict mode error: Locale 'ru': Strict mode error: Index out of bounds for list at path 'pages.10'...

# Attempting to use dot notation on a list wrapper raises AttributeError
try:
    _ = ru_translator_strict.pages.some_attribute
except AttributeError as e:
     print(f"Strict mode error: {e}")
     # Example Output: Strict mode error: 'LocaleList' object has no attribute 'some_attribute' # (Standard Python error)

# Attempting to use index notation on a dictionary wrapper raises TypeError
try:
    _ = ru_translator_strict.messages[0]
except TypeError as e:
     print(f"Strict mode error: {e}")
     # Example Output: Strict mode error: 'LocaleNamespace' object is not subscriptable # (Standard Python error)

# Attempting to call a non-callable wrapper (__call__ defined to raise TypeError)
try:
    _ = ru_translator_strict.pages()
except TypeError as e:
     print(f"Strict mode error: {e}")
     # Example Output: Strict mode error: 'LocaleList' object at path 'pages' is not callable...

# Attempting to implicitly convert a non-value wrapper to string (__str__ defined to raise TypeError in strict)
try:
    print(ru_translator_strict.pages)
except TypeError as e:
     print(f"Strict mode error: {e}")
     # Example Output: Strict mode error: 'LocaleList' object at path 'pages' cannot be converted to string...

```

### 7. Handling Explicit `null` Values

If a key/path exists, but its value is explicitly set to `null` in the YAML file, accessing it will return `None`. In non-strict mode, this will also log a warning to distinguish it from a "not found" path.

Example `en.yaml` with null:
```yaml
explicit_null_key: null
nested:
  another_null: null
```

```python
# Using the non-strict data instance
en_translator = data_non_strict['en']

# Accessing the null value returns None and logs a warning
import logging # Ensure logging is imported for basicConfig if needed
logging.basicConfig(level=logging.WARNING) # Basic setup to see warnings

# Use an appropriate method for capturing logs in tests if needed.
# In standard runtime, warnings will go to console/configured handler.
value1 = en_translator.explicit_null_key
value2 = en_translator.nested.another_null

print(f"Value 1: {value1}") # Output: Value 1: None
print(f"Value 2: {value2}") # Output: Value 2: None
# A warning will also appear in the logs, e.g.:
# WARNING:src.doti18n.locale_translator:Locale 'en': key/index path 'explicit_null_key' has an explicit None value.
# WARNING:src.doti18n.locale_translator:Locale 'en': key/index path 'nested.another_null' has an explicit None value.
```
In strict mode, accessing an explicit `null` value will simply return `None` without raising an exception (as the path *was* found).

## Optional Dependencies

*   **Babel**: Required for correct pluralization handling across different languages. Install with `pip install doti18n[pluralization]`.

## Project Status

This project is in an early stage of development (**Alpha**). The API may change in future versions before reaching a stable (1.0.0) release. Any feedback and suggestions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/darkj3suss/dot-i18n/blob/main/LICENSE) file for details.

## Contact

If you have questions, feel free to open an issue on GitHub.
Or you can message me on [Telegram](https://t.me/darkjesuss)
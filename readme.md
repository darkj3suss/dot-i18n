# doti18n [![PyPI version](https://badge.fury.io/py/doti18n.svg)](https://pypi.org/project/dot-i18n/) [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/darkj3suss/dot-i18n/blob/main/LICENSE)

Simple and intuitive Python library for loading localizations from YAML files and accessing them easily using dot notation, with powerful support for plural forms.

## Description

doti18n provides a convenient way to manage your application's localization strings. By loading data from standard YAML files, the library allows you to access nested translations using a simple dot syntax (`messages.status.online`), similar to accessing object attributes or dictionary keys in some other languages/frameworks.

Special attention is given to pluralization support using the [Babel](https://babel.pypa.io/en/stable/) library, which is critical for correct localization across different languages. An automatic fallback mechanism to the default locale's value is also implemented if a key is missing in the requested locale.

The library is designed for ease of use and performance (data is loaded once during initialization).

## Features

*   Loading localization data from YAML files.
*   Intuitive access to nested keys using dot notation (`data.section.key`).
*   Pluralization support for count-dependent strings (requires `Babel`).
*   Automatic fallback to the default locale if a key is missing in the current locale.
*   Returns `None` and logs a warning if a key is missing in both the current and default locales.
*   Caching of loaded data and translator objects for efficient access.

## Installation

doti18n is available on [PyPI](https://pypi.org/project/doti18n/).

Install the basic version (without pluralization support):

```bash
pip install doti18n
```

For pluralization support (recommended), install with the optional `pluralization` dependency:

```bash
pip install doti18n[pluralization]
```

**Note:** Pluralization support is implemented using the [Babel](https://babel.pypa.io/) library. If you install doti18n without the `[pluralization]` optional dependency, pluralization functionality will be limited or unavailable, and the library will log a warning about the missing Babel dependency.

## Usage

### 1. Localization File Structure

Place your YAML localization files in a dedicated directory. The filename (without the extension) should correspond to the locale code (e.g., `en.yaml`, `ru.yml`, `fr.yaml`).

Example `locales/` directory structure:

```
locales/
├── en.yaml
└── ru.yml
```

Example `en.yaml` content:

```yaml
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
```

Example `ru.yml` content:

```yaml
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
```

### 2. Initialize `LocaleData`

Create an instance of the `LocaleData` class, specifying the path to your localization files directory and the default locale code.

```python
from doti18n import LocaleData
import os # For example

# Assuming your localization files are in a 'locales' subdirectory
locales_dir = os.path.join(os.path.dirname(__file__), 'locales_example') # Use your actual path

data = LocaleData(locales_dir, default_locale='en')
```

### 3. Accessing Translations (Dot Notation)

You can retrieve a translator object for a specific locale by accessing the `LocaleData` instance like a dictionary. Then, use dot notation to access nested keys.

```python
# Get the translator for the English locale
# You also can use some like data["en"].messages.greeting
en_translator = data["en"]


# Access simple strings
print(en_translator.messages.greeting)           # Output: Hello!
print(en_translator.messages.status.online)      # Output: You are online.

# Access a translation in Russian
ru_translator = data["ru"]
print(ru_translator.messages.greeting)           # Output: Привет!
print(ru_translator.messages.status.online)      # Output: Вы онлайн.

# Handling placeholders in strings (use the .format() method)
# print(en_translator.messages.welcome_user.format(username="Alice")) # Desired: Welcome, Alice!
# For now, you can get the string and format it separately:
welcome_template = en_translator.messages.welcome_user
print(welcome_template.format(username="Alice")) # Output: Welcome, Alice!
```

### 4. Working with Pluralization

If a key's value is a dictionary with plural form keys (`one`, `few`, `many`, `other`, etc.), accessing this key via dot notation will return a **callable object**. Call this object, passing the number (`count`) and, optionally, other arguments for string formatting.

**Requires Babel (`pip install doti18n[pluralization]`)**

```python
# Get the translator for the English locale
en_translator = data['en']

# The 'apple' key returns a callable object for plural forms
apple_plural_en = en_translator.items.apple

# Call it, passing the count
print(apple_plural_en(1)) # Output: You have 1 apple.
print(apple_plural_en(5)) # Output: You have 5 apples.

# Call it with other formatting arguments
print(apple_plural_en(1, count=1)) # Pass count explicitly if needed for formatting, abs(count) is passed by default

# Get the translator for the Russian locale
ru_translator = data['ru']
apple_plural_ru = ru_translator.items.apple

print(apple_plural_ru(1))   # Output: У вас 1 яблоко.
print(apple_plural_ru(3))   # Output: У вас 3 яблока.
print(apple_plural_ru(5))   # Output: У вас 5 яблок.
print(apple_plural_ru(21))  # Output: У вас 21 яблоко.
print(apple_plural_ru(100)) # Output: У вас 100 яблок.

# Passing additional formatting arguments
# For example, if the template is "{count} {item_name}"
# print(apple_plural_ru(3, item_name="красненьких")) # Desired Output: "У вас 3 красненьких яблока"
# Currently, only 'count' is available by default for formatting
```
*Note: Currently, only `count` (the absolute value of the number passed) is available for formatting within plural form strings. If you need other variables, you would need to retrieve the template string and format it separately.*

### 5. Fallback to Default Locale

If a key is missing in the requested locale, the library will attempt to find it in the default locale specified during `LocaleData` initialization.

```python
# ru.yml does not contain the key messages.status.offline
# Attempting to get it in Russian:
ru_translator = data['ru']
print(ru_translator.messages.status.offline) # Output: You are offline. (value from en.yaml)

# ru.yml does not contain the key messages.welcome_user
print(ru_translator.messages.welcome_user) # Output: Welcome, {username}! (value from en.yaml)
```

### 6. Handling Missing Keys

If a key is missing in both the current locale and the default locale, accessing it will return `None`, and the library will log a warning using the standard `logging` module.

```python
# The key 'non_existent_key' does not exist in either en.yaml or ru.yml
ru_translator = data['ru']
value = ru_translator.this.key.does.not.exist
print(value) # Output: None
# A warning will also appear in the logs:
# WARNING:doti18n.locale_translator:Locale 'ru': key 'this.key.does.not.exist' not found in translations...
```
**Important:** To see these warnings, ensure your application has configured logging. A basic setup is `logging.basicConfig(level=logging.INFO)`.

## Optional Dependencies

*   **Babel**: Required for correct pluralization handling across different languages. Install with `pip install doti18n[pluralization]`.

## Project Status

This project is in an early stage of development (**Alpha**). The API may change in future versions before reaching a stable (1.0.0) release. Any feedback and suggestions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/darkj3suss/dot-i18n/blob/main/LICENSE) file for details.

## Contact

If you have questions, feel free to open an issue on GitHub.
Or you can message me on [Telegram](https://t.me/darkjesuss)
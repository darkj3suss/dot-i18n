# examples/strict_mode.py
import os
import logging
from src.doti18n import LocaleData

# Configure logging (warnings might still appear from LocaleData loading issues, but not missing paths)
logging.basicConfig(level=logging.INFO)

# Assuming this script is in the 'examples' directory relative to the project root
examples_dir = os.path.dirname(__file__)
locales_dir = os.path.join(examples_dir, 'locales')

print(f"Loading locales from: {locales_dir}")

# Initialize LocaleData in STRICT mode
# noinspection PyArgumentEqualDefault
data_strict = LocaleData(locales_dir, default_locale='en', strict=True)

print("\n--- Strict Mode Examples ---")

en_translator_strict = data_strict["en"]
ru_translator_strict = data_strict["ru"]

# 1. Accessing Missing Paths (Should raise exceptions)
print("\n--- Missing Paths (Strict) ---")
try:
    print("Accessing missing key:", ru_translator_strict.this.key.does.no.exist)
except AttributeError as e:
    print(f"Caught expected error for missing key: {e}")

try:
    print("Accessing out-of-bounds index:", en_translator_strict.pages[10])
except IndexError as e:
    print(f"Caught expected error for out-of-bounds index: {e}")

# 2. Incorrect Usage of Wrappers (Should raise standard Python errors or TypeErrors)
print("\n--- Incorrect Wrapper Usage (Strict) ---")

# Attempting dot notation on a list wrapper (standard Python AttributeError)
pages_list = en_translator_strict.pages
print(f"Type of 'pages': {type(pages_list)}")
try:
    print("Accessing attribute on LocaleList:", pages_list.some_attribute)
except AttributeError as e:
    print(f"Caught expected error for LocaleList attribute access: {e}")

# Attempting index notation on a dictionary/namespace wrapper (standard Python TypeError)
messages_namespace = en_translator_strict.messages
print(f"Type of 'messages': {type(messages_namespace)}")
try:
    print("Accessing index on LocaleNamespace:", messages_namespace[0])
except TypeError as e:
    print(f"Caught expected error for LocaleNamespace index access: {e}")

# Attempting to call a wrapper object (defined to raise TypeError)
try:
    print("Calling LocaleList:", pages_list())
except TypeError as e:
    print(f"Caught expected error for calling LocaleList: {e}")

try:
    print("Calling LocaleNamespace:", messages_namespace())
except TypeError as e:
    print(f"Caught expected error for calling LocaleNamespace: {e}")

# Attempting implicit string conversion of a wrapper object (__str__ raises TypeError in strict)
try:
    print("Implicit string conversion of LocaleList:", pages_list)
except TypeError as e:
    print(f"Caught expected error for LocaleList string conversion: {e}")

try:
    # Note: LocaleNamespace.__str__ *does* return a string representation in strict, this won't raise.
    print("Implicit string conversion of LocaleNamespace:", messages_namespace)
except TypeError as e:  # This block likely won't be reached for LocaleNamespace
    print(f"Caught unexpected error for LocaleNamespace string conversion: {e}")

# 3. Accessing Explicit None (Should NOT raise exceptions, returns None)
print("\n--- Explicit None (Strict) ---")
# Create a locale with explicit null values
# (LocaleData instance needs to be reloaded or created to include this file)
# For simplicity, let's assume 'en.yaml' already has 'explicit_null_key: null'
# (as added in the README example and examples/locales/en.yaml)

try:
    value = en_translator_strict.explicit_null_key
    print(f"Value of explicit_null_key: {value}")
    if value is None:
        print("Confirmed: Value is None.")
except Exception as e:
    print(f"Caught unexpected error accessing explicit null: {e}")

try:
    value = en_translator_strict.nested.another_null
    print(f"Value of nested.another_null: {value}")
    if value is None:
        print("Confirmed: Value is None.")
except Exception as e:
    print(f"Caught unexpected error accessing nested explicit null: {e}")

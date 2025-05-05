# examples/null_handling.py

import os
import logging
from src.doti18n import LocaleData
from src.doti18n.wrapped import NoneWrapper  # Import NoneWrapper for isinstance check if desired

# Configure logging to see WARNING messages
# In a real application, you'd configure logging more verbosely
logging.basicConfig(level=logging.WARNING, format='%(levelname)s:%(name)s:%(message)s')

# Assuming this script is in the 'examples' directory relative to the project root
examples_dir = os.path.dirname(__file__)
# Go up one level to find the locales directory
project_root = os.path.dirname(examples_dir)
locales_dir = os.path.join(project_root, 'examples',
                           'locales')  # Ensure the path to locales/ inside examples/ is correct

print(f"Loading locales from: {locales_dir}")

# Initialize LocaleData in non-strict mode (default)
# noinspection PyArgumentEqualDefault
data_non_strict = LocaleData(locales_dir, default_locale='en', strict=False)

print("\n--- Explicit Null Handling (Non-Strict) ---")

en_translator = data_non_strict["en"]

# Accessing a key with an explicit null value in YAML
# In non-strict mode, this returns None and logs a warning
print("Accessing explicit_null_key...")
value = en_translator.explicit_null_key
print(f"Value: {value}")  # Output: Value: None

print("\nAccessing nested.another_null...")
value = en_translator.nested.another_null
print(f"Value: {value}")  # Output: Value: None

# In both cases above, a warning will appear in the logs like:
# WARNING:src.doti18n.locale_translator:Locale 'en': key/index path 'explicit_null_key' has an explicit None value.

print("\n--- Contrast with Missing Path (Non-Strict) ---")
# This case logs a *different* warning message compared to explicit null
print("Accessing missing...")
value = en_translator.missing
# print(value) # The output will show the NoneWrapper representation
print(f"Value: {value}")
# Expected output (approximate): Value: NoneWrapper('en': missing)
# A warning will appear in the logs like:
# WARNING:src.doti18n.locale_translator:Locale 'en': key/index path 'missing' not found... None will be returned.

# You can check it using == None (as recommended in the README)
# Or `not value`
if value == None:
    print("Checked with == None: Key is not found.")

# Or using isinstance (for a more explicit check on the wrapper type)
if isinstance(value, NoneWrapper):
    print("Checked with isinstance(value, NoneWrapper): Value is a NoneWrapper.")

print("\n--- Explicit Null Handling (Strict) ---")

# Initialize in strict mode
# noinspection PyArgumentEqualDefault
data_strict = LocaleData(locales_dir, default_locale='en', strict=True)
en_translator_strict = data_strict["en"]

# In strict mode, accessing explicit null returns None WITHOUT raising an exception
try:
    value = en_translator_strict.explicit_null_key
    print(f"Value of explicit_null_key (strict): {value}")
    if value is None:  # Here is None is correct, as it returns the actual None
        print("Confirmed (strict): Value is None.")
except Exception as e:  # We should not catch any exceptions here
    print(f"Caught unexpected error accessing explicit null in strict mode: {e}")

# Contrast with Missing Path in Strict Mode (raises exception)
print("\n--- Contrast with Missing Path (Strict) ---")
try:
    print("Accessing missing path (strict)...")
    value = en_translator_strict.missing.non_existent_key
except AttributeError as e:
    print(f"Caught expected error for missing key in strict mode: {e}")

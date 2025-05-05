# examples/null_handling.py
import os
import logging
from src.doti18n import LocaleData

# You might need to explicitly import the logger to capture its output in tests
# from src.doti18n.locale_translator import logger as translator_logger

# Configure logging to see WARNING messages
logging.basicConfig(level=logging.WARNING)

# Assuming this script is in the 'examples' directory relative to the project root
examples_dir = os.path.dirname(__file__)
locales_dir = os.path.join(examples_dir, 'locales')

print(f"Loading locales from: {locales_dir}")

# Initialize LocaleData in non-strict mode (default)
# noinspection PyArgumentEqualDefault
data_non_strict = LocaleData(locales_dir, default_locale='en', strict=False)

print("\n--- Explicit Null Handling (Non-Strict) ---")

en_translator = data_non_strict["en"]

# Accessing a key with explicit null value in YAML
# In non-strict mode, this returns None and logs a warning
print("Accessing explicit_null_key...")
# Use a logging capture mechanism if running this in a testing context
# For a simple script, the warning will print to console if level is WARNING or lower
value = en_translator.explicit_null_key
print(f"Value: {value}")  # Output: None

print("\nAccessing nested.another_null...")
value = en_translator.nested.another_null
print(f"Value: {value}")  # Output: None

print("\n--- Contrast with Missing Path (Non-Strict) ---")
# This logs a *different* warning message compared to explicit null
print("Accessing missing...")
value = en_translator.missing
print(f"Value: {value}")  # Output: None

print("\n--- Explicit Null Handling (Strict) ---")

# Initialize in strict mode
# noinspection PyArgumentEqualDefault
data_strict = LocaleData(locales_dir, default_locale='en', strict=True)
en_translator_strict = data_strict["en"]

# In strict mode, accessing explicit null returns None WITHOUT raising an exception
try:
    value = en_translator_strict.explicit_null_key
    print(f"Value of explicit_null_key (strict): {value}")
    if value is None:
        print("Confirmed: Value is None.")
except Exception as e:  # Should not catch any exception here
    print(f"Caught unexpected error accessing explicit null in strict mode: {e}")

# Contrast with Missing Path in Strict Mode (raises exception)
print("\n--- Contrast with Missing Path (Strict) ---")
try:
    print("Accessing missing path (strict)...")
    value = en_translator_strict.missing.non_existent_key
except AttributeError as e:
    print(f"Caught expected error for missing key in strict mode: {e}")

import sys
import gettext

# Console thing
sys.stdout.reconfigure(encoding="utf-8")

# Constants for font styles and colors
LARGE_FONT = ("Source Sans Pro", 20, "bold")
SMALL_FONT = ("Source Sans Pro", 14)
SMALLEST_FONT = ("Source Sans Pro", 12)

# Language of the App
lang_code = "ru"  # Desired language code
localedir = "locales"  # Path to locales directory
domain = "base"  # Name of the .po/.mo files

translation = gettext.translation(
    domain, localedir=localedir, languages=["en", "ru"], fallback=True
)
translation.install()

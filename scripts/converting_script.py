import yaml


class UnitConverter:
    def __init__(self):
        self.unit_files = {
            "temperature": "data/temperature_units.yaml",
            "area": "data/area_units.yaml",
            "length": "data/length_units.yaml",
            "volume": "data/volume_units.yaml",
            "time": "data/time_units.yaml",
            "weight": "data/weight_units.yaml",
        }
        self.default_category = next(
            iter(self.unit_files)
        )  # Getting first key from dict

    def get_unit_formulas(self, category=None):
        """Get the unit data in a given category for easier work and set default category."""
        if category is None:
            category = self.default_category

        category_key = self._translate_category(category)
        unit_data = self._load_unit_data(category_key)
        units = unit_data.get(f"{category_key}_units", [])
        return {
            unit["name"]: {
                k: v for k, v in unit.items() if k.startswith("to_") or k == "symbol"
            }
            for unit in units
        }

    def _translate_category(self, category):
        """Translate category name to English equivalent if in Russian."""
        translation_map = {
            "температура": "temperature",
            "площадь": "area",
            "длина": "length",
            "объём": "volume",
            "время": "time",
            "вес": "weight",
        }
        return translation_map.get(category.lower(), category.lower())

    def _load_unit_data(self, category_key):
        """Load and return the conversion table for a given unit type."""
        file_path = self.unit_files.get(category_key)
        if not file_path:
            raise FileNotFoundError(f"No file path found for '{category_key}'.")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing the YAML file: {e}")


# Debug section
if __name__ == "__main__":
    import pprint

    converter = UnitConverter()
    pprint.pprint(converter.get_unit_formulas())

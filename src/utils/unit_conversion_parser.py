import yaml


class UnitConversionParser:
    def __init__(self):
        """
        Initializes the UnitConversionParser with a dictionary of unit files and
        sets the default category to the first key in the dictionary.
        """
        self.unit_files = {
            "temperature": "src/data/temperature_units.yaml",
            "area": "src/data/area_units.yaml",
            "length": "src/data/length_units.yaml",
            "volume": "src/data/volume_units.yaml",
            "time": "src/data/time_units.yaml",
            "mass": "src/data/mass_units.yaml",
            "speed": "src/data/speed_units.yaml",
            "force": "src/data/force_units.yaml",
            "fuel_consumption": "src/data/fuel_consumption_units.yaml",
            "numeral_systems": "src/data/numeral_systems_units.yaml",
            "pressure": "src/data/pressure_units.yaml",
            "energy": "src/data/energy_units.yaml",
            "power": "src/data/power_units.yaml",
            "angles": "src/data/angles_units.yaml",
            "digital_data": "src/data/digital_data_units.yaml",
        }
        self.default_category = next(
            iter(self.unit_files)
        )  # Getting first key from dict

    def get_unit_formulas(self, category=None):
        """
        Fetches the unit data in a given category for easier work and sets default category.

        Args:
            category (str): The category of units to fetch formulas for. If not provided, uses default category.

        Returns:
            dict: A dictionary of units in the category with their conversion formulas.
        """
        if category is None:
            category = self.default_category

        category_key = category.lower().replace(" ", "_")
        unit_data = self._load_unit_data(category_key)
        units = unit_data.get(f"{category_key}_units", [])
        return {
            unit["name"]: {
                k: v for k, v in unit.items() if k.startswith("to_") or k == "symbol"
            }
            for unit in units
        }

    def _load_unit_data(self, category_key):
        """
        Loads unit data from the file corresponding to the given category key.

        Args:
            category_key (str): The key representing the category of units.

        Raises:
            ValueError: If there is an error parsing the YAML file.

        Returns:
            dict: A dictionary containing the unit data.
        """
        file_path = self.unit_files.get(
            category_key, self.unit_files.get(self.default_category)
        )
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing the YAML file: {e}")


# Debug section
if __name__ == "__main__":
    import pprint

    converter = UnitConversionParser()
    pprint.pprint(converter.get_unit_formulas())

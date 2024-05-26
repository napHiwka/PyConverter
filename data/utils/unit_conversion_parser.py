import yaml


class UnitConversionParser:
    def __init__(self):
        """
        Initializes the UnitConversionParser with a dictionary of unit files and
        sets the default category to the first key in the dictionary.
        """
        self.unit_files = {
            "temperature": "data/units/temperature_units.yaml",
            "area": "data/units/area_units.yaml",
            "length": "data/units/length_units.yaml",
            "volume": "data/units/volume_units.yaml",
            "time": "data/units/time_units.yaml",
            "mass": "data/units/mass_units.yaml",
            "speed": "data/units/speed_units.yaml",
            "force": "data/units/force_units.yaml",
            "fuel_consumption": "data/units/fuel_consumption_units.yaml",
            "numeral_systems": "data/units/numeral_systems_units.yaml",
            "pressure": "data/units/pressure_units.yaml",
            "energy": "data/units/energy_units.yaml",
            "power": "data/units/power_units.yaml",
            "angles": "data/units/angles_units.yaml",
            "digital_data": "data/units/digital_data_units.yaml",
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
    converter = UnitConversionParser()
    print(converter.get_unit_formulas())

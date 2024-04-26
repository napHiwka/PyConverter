import numexpr
import customtkinter as ctk
from src.utils.unit_conversion_parser import UnitConversionParser


class UnitConversionUpdater:
    def __init__(self, entries_list):
        self.entries = entries_list
        self.converter = UnitConversionParser()
        self.unit_formulas = self.converter.get_unit_formulas()
        self.entry_components = self._create_entry_components()
        self._load_default_category()

    def _load_default_category(self):
        """Load the default category."""
        self._refresh_entries_with_current_units()

    def load_category_from_button(self, category):
        """Load a new category when a button is clicked."""
        self.unit_formulas = self.converter.get_unit_formulas(category)
        self.entry_components = self._create_entry_components()
        self._refresh_entries_with_current_units()

    def _refresh_entries_with_current_units(self):
        """Refresh and update the entry fields with unit data from the current
        category."""
        for entry_component in self.entry_components:
            self._unbind_and_clear_entry(entry_component)
            self._bind_and_fill_entry(entry_component)

    def _unbind_and_clear_entry(self, entry_component):
        """Unbind the KeyRelease event and clear the entry fields."""
        (entry_widget, unit_symbol_label, unit_name_label, *rest) = entry_component
        entry_widget.unbind("<KeyRelease>")
        entry_widget.delete(0, ctk.END)
        unit_symbol_label.configure(text="")
        unit_name_label.configure(text="")

    def _bind_and_fill_entry(self, entry_component):
        """Bind the KeyRelease event and fill the entry fields with unit data."""
        (
            entry_widget,
            unit_symbol_label,
            unit_name_label,
            entry_string_var,
            unit_name,
        ) = entry_component
        if unit_name:
            entry_widget.bind(
                "<KeyRelease>",
                lambda e: self.update_related_unit_entries(
                    e, unit_name, entry_string_var
                ),
            )
            unit_name_label.configure(text=unit_name)
            unit_symbol_label.configure(text=self.unit_formulas[unit_name]["symbol"])

    def _create_entry_components(self):
        """Create entry components and assign unit names to them."""
        unit_names = tuple(self.unit_formulas.keys())
        return [
            self._create_entry_component(
                components, unit_names[i] if i < len(unit_names) else None
            )
            for i, components in enumerate(self.entries)
        ]

    @staticmethod
    def _create_entry_component(components, unit_name):
        """Create an entry component with unit name."""
        entry_widget, unit_symbol_label, unit_name_label, entry_string_var = components
        return (
            entry_widget,
            unit_symbol_label,
            unit_name_label,
            entry_string_var,
            unit_name,
        )

    def update_related_unit_entries(self, event, source_unit, source_entry_var):
        """Update all related unit entries based on the value of the source entry."""
        try:
            value = float(source_entry_var.get())
            for _, _, _, target_var, target_unit in self.entry_components:
                if target_unit and target_unit != source_unit:
                    self._update_target_entry(
                        value, source_unit, target_var, target_unit
                    )
        except ValueError:
            self._clear_non_source_entries(source_unit)

    def _update_target_entry(self, value, source_unit, target_var, target_unit):
        """Update a target entry with the converted value."""
        target_unit = target_unit.replace(" ", "_")
        conversion_key = "to_" + target_unit.lower()
        conversion_formula = self.unit_formulas[source_unit].get(conversion_key)
        if conversion_formula:
            converted_value = numexpr.evaluate(conversion_formula.format(val=value))
            target_var.set(str(converted_value))
        else:
            target_var.set("")

    def _clear_non_source_entries(self, source_unit):
        """Clear all non-source entries."""
        for _, _, _, target_var, target_unit in self.entry_components:
            if target_unit != source_unit:
                target_var.set("")

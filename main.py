import pprint

import customtkinter as ctk

from scripts.converting_script import UnitConverter
from scripts.settings import *


class RightPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self._configure_grid()
        self.entries = (
            self._create_entries()
        )  # Get te dict of entries (key: (row, column), value: (entry, entry_symbol,entry_text, entry_var))

    def _configure_grid(self):
        # configure columns
        self.grid_columnconfigure(0, weight=25, uniform="A")
        self.grid_columnconfigure(1, weight=5, uniform="A")
        self.grid_columnconfigure(2, weight=25, uniform="A")
        self.grid_columnconfigure(3, weight=5, uniform="A")

        # configure rows
        self.grid_rowconfigure(tuple(range(8)), weight=1, uniform="A")

    def _create_entries(self):
        entries_dict = {}

        # Iterate through rows, starting from 0 and incrementing by 2
        for row in range(0, 16, 2):
            # Iterate through columns, every alternate column
            for column in [0, 2]:
                # Create entry variable
                entry_var = ctk.StringVar()

                # Create label for entry text
                entry_text = ctk.CTkLabel(
                    self,
                    text="",
                    height=20,
                    font=SMALLEST_FONT,
                    text_color=("gray52", "gray62"),
                )
                entry_text.grid(
                    row=row, column=column, padx=(0, 5), pady=10, sticky="se"
                )

                # Create entry field
                entry = ctk.CTkEntry(
                    self,
                    width=220,
                    height=40,
                    justify="right",
                    textvariable=entry_var,
                )
                entry.grid(row=row + 1, column=column, sticky="nse")

                # Create label for entry symbol
                entry_symbol = ctk.CTkLabel(self, text="", font=SMALL_FONT, width=10)
                entry_symbol.grid(
                    row=row + 1, column=column + 1, sticky="w", padx=(5, 0)
                )

                # Add entry, entry symbol, and entry text to entries_dict
                entries_dict[(row // 2, column)] = (
                    entry,
                    entry_symbol,
                    entry_text,
                    entry_var,
                )  # Use row // 2 to keep the row index consistent with the original layout

        return entries_dict


class LeftPanel(ctk.CTkFrame):
    def __init__(self, parent, right_panel):
        super().__init__(parent)
        self._configure_grid()
        self._create_widgets()
        self.unit_data_handler = UnitDataHandler(right_panel.entries)

    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=1, uniform="A")
        self.grid_rowconfigure(tuple(range(11)), weight=1, uniform="A")

    def _create_widgets(self):
        self._create_label(text="Тип конвертации", font=LARGE_FONT)  # Title creation
        self._add_conversion_buttons()  # Button creation
        self._create_appearance_mode_optionmenu()  # Dropdown appearance creation

    def _create_label(self, text, font=SMALL_FONT, row=0, column=0, **grid_kwargs):
        ctk.CTkLabel(self, text=text, font=font).grid(
            row=row, column=column, **grid_kwargs
        )

    def _add_conversion_buttons(self):
        # List of conversion types to add buttons for
        conversion_types = [
            "Температура",
            "Площадь",
            "Длина",
            "Объём",
            "Время",
            "Вес",
        ]  # TODO: 01

        # Function to create a conversion button
        def _create_button(text, row):
            ctk.CTkButton(
                self,
                text=text,
                font=SMALL_FONT,
                command=lambda t=text: self._button_event(t),
            ).grid(row=row, column=0, padx=20, pady=0)

        # Add buttons for each conversion type
        for row, conversion_type in enumerate(conversion_types, start=1):
            _create_button(conversion_type, row=row)

    def _create_appearance_mode_optionmenu(self):

        def change_appearance_mode(new_mode):
            mode_mapping = {
                "Светлый": "Light",
                "Тёмный": "Dark",
                "Системный": "System",
            }  # TODO: 02
            ctk.set_appearance_mode(mode_mapping.get(new_mode, "System"))

        self._create_label(text="Внешний вид:", font=SMALL_FONT, row=9, pady=(0, 0))
        appearance_options = ("Светлый", "Тёмный", "Системный")  # TODO: 02

        self.appearance_variable = ctk.StringVar(value=appearance_options[2])
        ctk.CTkOptionMenu(
            self,
            values=appearance_options,
            variable=self.appearance_variable,
            dropdown_font=SMALLEST_FONT,
            command=change_appearance_mode,
        ).grid(row=10, column=0, sticky="s", pady=(0, 10))

    def _button_event(self, category_type):
        pprint.pprint(f"Conversion type selected: {category_type}")  # TODO: Remove
        self.unit_data_handler.load_category_from_button(category_type)


class UnitDataHandler:
    def __init__(self, entries_dict):
        self.entries = entries_dict
        self.converter = UnitConverter()
        self.unit_formulas = (
            self.converter.get_unit_formulas()
        )  # Get formulas from the default category

        self._load_default_category()  # Load the default category

    def _load_default_category(self):
        self._refresh_entries_with_current_units()

    def load_category_from_button(self, category):
        self.unit_formulas = self.converter.get_unit_formulas(category)
        self._refresh_entries_with_current_units()

    def _assign_unit_names_to_entries(self):
        """Assign unit names to entry components and store them as attributes for access."""
        self.unit_names = tuple(self.unit_formulas.keys())
        self.entry_components = []

        for index, components in enumerate(self.entries.values()):
            entry_widget, unit_symbol_label, unit_name_label, entry_string_var = (
                components
            )
            unit_name = self.unit_names[index] if index < len(self.unit_names) else None
            self.entry_components.append(
                (
                    entry_widget,
                    unit_symbol_label,
                    unit_name_label,
                    entry_string_var,
                    unit_name,
                )
            )

    def _refresh_entries_with_current_units(self):
        self._assign_unit_names_to_entries()  # Ensure unit names are assigned to entries

        """Refresh and update the entry fields with unit data from the current category."""
        for (
            entry_widget,
            unit_symbol_label,
            unit_name_label,
            entry_string_var,
            unit_name,
        ) in self.entry_components:
            if unit_name:
                entry_widget.delete(0, ctk.END)
                entry_widget.bind(
                    "<KeyRelease>",
                    lambda e, unit=unit_name, entry_var=entry_string_var: self.update_related_unit_entries(
                        e, unit, entry_var
                    ),
                )
                unit_name_label.configure(text=unit_name)
                unit_symbol_label.configure(
                    text=self.unit_formulas[unit_name]["symbol"]
                )
            else:
                entry_widget.unbind("<KeyRelease>")
                unit_name_label.configure(text="")
                unit_symbol_label.configure(text="")

    def update_related_unit_entries(self, event, source_unit, source_entry_var):
        """
        Update all related unit entry fields based on the value of the source entry.

        Args:
            event: The key release event triggering the update.
            source_unit: The unit of the source entry that was updated.
            source_entry_var: The tkinter variable associated with the source entry.

        This method is called when a key is released in any of the unit entry widgets.
        It reads the value from the source entry and calculates the corresponding
        values for all other unit entries using the conversion formulas defined in
        `self.unit_formulas`. If the value in the source entry is not a valid float,
        it clears the non-source entries.
        """
        try:
            # Attempt to parse the value as a float
            value = float(source_entry_var.get())

            for _, _, _, target_var, target_unit in self.entry_components:
                if target_unit in (source_unit, None):
                    # Skip the source unit entry or if the target unit is not defined
                    continue

                # Get the conversion formula from source unit to target unit
                conversion_key = "to_" + target_unit.lower()
                conversion_formula = self.unit_formulas[source_unit].get(conversion_key)

                if conversion_formula is not None:
                    # Evaluate the conversion formula to get the new value
                    converted_value = eval(
                        conversion_formula.replace("${val}", str(value))
                    )
                    target_var.set(str(converted_value))
                else:
                    # Clear the target entry if no conversion formula is available
                    target_var.set("")

        except ValueError:
            # If the input is not a valid number, clear all non-source entries
            for _, _, _, target_var, target_unit in self.entry_components:
                if target_unit != source_unit:
                    target_var.set("")


class MainConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Converter")
        self._setup_ui()
        self._run()

    def _setup_ui(self):
        self._setup_window()
        self._setup_appearance()
        self._layout_panels()

    def _setup_window(self):
        self.geometry("800x500")
        self.resizable(0, 0)

    def _setup_appearance(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

    def _layout_panels(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.right_panel = RightPanel(self)
        self.right_panel.grid(row=0, column=1, padx=5, sticky="nsew")

        self.left_panel = LeftPanel(self, self.right_panel)
        self.left_panel.grid(row=0, column=0, sticky="nsw")

    def _run(self):
        self.mainloop()


if __name__ == "__main__":
    MainConverter()

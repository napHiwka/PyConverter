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
                entry.bind(
                    "<KeyRelease>", lambda e, var=entry_var: print(var.get())
                )  # TODO: Remove

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

    def _refresh_entries_with_current_units(self):
        """Refresh the entry fields with the units from the current selected category."""
        unit_names = list(self.unit_formulas.keys())
        for index, components in enumerate(self.entries.values()):
            self._update_entry_with_unit_data(
                index, unit_names, components, self.unit_formulas
            )

    def _update_entry_with_unit_data(
        self, index, unit_names, components, unit_formulas
    ):
        """Update the entry fields with unit data based on the selected category.

        Args:
            index (int): The index of the current entry in the unit_names list.
            unit_names (list): List of unit names corresponding to the current category.
            components (tuple): Tuple containing the entry widgets and variable.
            unit_formulas (dict): Dictionary of unit formulas and symbols.
        """
        entry_widget, unit_symbol_label, unit_name_label, entry_string_var = components
        if index < len(
            unit_names
        ):  # Check if the index is within the bounds of the unit_names list
            entry_widget.delete(0, ctk.END)  # Clear the entry field from previous data
            entry_string_var = 0

            unit_name = unit_names[index]  # Get the unit name at the current index
            entry_widget.bind(
                "<KeyRelease>",
                lambda e, unit=unit_name: self._entry_key_release_handler(
                    e, unit, unit_formulas
                ),
            )
            unit_name_label.configure(text=unit_name)
            unit_symbol_label.configure(text=unit_formulas[unit_name]["symbol"])
            print("Hi")
        else:  # If the index is out of bounds, clear the entry field
            unit_name_label.configure(text="")
            unit_symbol_label.configure(text="")

    def _entry_key_release_handler(self, event, unit, unit_formulas):
        pass


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

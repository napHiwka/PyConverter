import pprint

import customtkinter as ctk

from scripts.converting_script import UnitConverter
from scripts.settings import *


class LeftPanel(ctk.CTkFrame):
    def __init__(self, parent, right_panel):
        super().__init__(parent)
        self.right_panel = right_panel
        self.converter = UnitConverter()
        self._configure_grid()
        self._create_widgets()

    def _configure_grid(self):
        self._configure_columns(1)
        self._configure_rows(11)

    def _configure_columns(self, num_columns):
        for i in range(num_columns):
            self.grid_columnconfigure(i, weight=1, uniform="A")

    def _configure_rows(self, num_rows):
        for i in range(num_rows):
            self.grid_rowconfigure(i, weight=1, uniform="A")

    def _create_widgets(self):
        self._create_label("Тип конвертации", LARGE_FONT, row=0)  # Title creation
        self._create_conversion_buttons()
        self._create_appearance_mode_optionmenu()

    def _create_label(self, text, font, row, column=0, **grid_kwargs):
        label = ctk.CTkLabel(self, text=text, font=font)
        label.grid(row=row, column=column, **grid_kwargs)

    def _create_conversion_buttons(self):
        conversion_types = ["Температура", "Площадь", "Длина", "Объём", "Время", "Вес"]

        def _create_button(text, row):
            button = ctk.CTkButton(
                self,
                text=text,
                font=SMALL_FONT,
                command=lambda t=text: self._button_event(t),
            )
            button.grid(row=row, column=0, padx=20, pady=0)

        for index, conversion_type in enumerate(conversion_types, start=1):
            _create_button(conversion_type, row=index)

    def _create_appearance_mode_optionmenu(self):
        self._create_label("Внешний вид:", SMALL_FONT, row=9, pady=(0, 0))
        appearance_options = ["Светлый", "Тёмный", "Системный"]

        self.appearance_var = ctk.StringVar(value="Системный")
        optionmenu = ctk.CTkOptionMenu(
            self,
            values=appearance_options,
            variable=self.appearance_var,
            dropdown_font=SMALLEST_FONT,
            command=self._change_appearance_mode,
        )
        optionmenu.grid(row=10, column=0, sticky="s", pady=(0, 10))

    def _change_appearance_mode(self, new_mode):
        mode_mapping = {"Светлый": "Light", "Тёмный": "Dark", "Системный": "System"}
        ctk.set_appearance_mode(mode_mapping.get(new_mode, "System"))

    def _button_event(self, category_type):
        pprint.pprint(f"Conversion type selected: {category_type}")
        unit_formulas = self.converter.get_unit_formulas(category_type)
        self.right_panel.right_panel_events(unit_formulas)


class RightPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent, default_category="temperature"):
        super().__init__(parent)
        self._configure_grid()
        self.entries = self._create_entries()
        self.converter = UnitConverter()
        self.unit_data_handler = UnitDataHandler(self.converter)
        self._load_default_category(default_category)

    def _load_default_category(self, category):
        unit_formulas = self.unit_data_handler.get_unit_formulas(category)
        self.right_panel_events(unit_formulas)

    def right_panel_events(self, unit_formulas):
        self.unit_data_handler.update_entries_with_units(self.entries, unit_formulas)

    def _configure_grid(self):
        self._configure_columns(4)
        self._configure_rows(8)

    def _configure_columns(self, num_columns):
        for i in range(num_columns):
            weight = 25 if i in [0, 2] else 5
            self.grid_columnconfigure(i, weight=weight, uniform="A")

    def _configure_rows(self, num_rows):
        for i in range(num_rows):
            self.grid_rowconfigure(i, weight=1, uniform="A")

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
                    self, width=220, height=40, justify="right", textvariable=entry_var
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


class UnitDataHandler:
    def __init__(self, converter):
        self.converter = converter

    def get_unit_formulas(self, category):
        return self.converter.get_unit_formulas(category)

    def update_entries_with_units(self, entries, unit_formulas):
        unit_names = list(unit_formulas.keys())

        for index, (entry, entry_unit, entry_text, entry_var) in enumerate(
            entries.values()
        ):
            if index < len(unit_names):
                entry.delete(0, ctk.END)  # Cleaning prev result from prev category

                unit_name = unit_names[index]
                entry.bind(
                    "<KeyRelease>",
                    lambda e, unit_name=unit_name: self._entry_key_release_handler(
                        e, unit_name, unit_formulas
                    ),
                )

                entry_text.configure(text=unit_name)
                entry_unit.configure(text=unit_formulas[unit_name]["symbol"])
            else:
                entry_text.configure(text="")
                entry_unit.configure(text="")

    def _entry_key_release_handler(self, event, unit_name, unit_formulas):
        formula = unit_formulas.get(unit_name, {}).get("to_celsius")
        print(
            f"Unit formula for {unit_name}: {formula}"
        )  # Replace with actual logic to use formula


class MainConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Converter")
        self._setup_ui()

    def _setup_ui(self):
        self._setup_window()
        self._setup_appearance()
        self._layout_panels()
        self.mainloop()

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
        self.right_panel.configure(fg_color="transparent")
        self.right_panel.grid(row=0, column=1, padx=5, sticky="nsew")

        self.left_panel = LeftPanel(self, self.right_panel)
        self.left_panel.grid(row=0, column=0, sticky="nsw")


if __name__ == "__main__":
    MainConverter()

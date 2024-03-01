import customtkinter as ctk
from scripts.settings import *
from scripts.unit_conversion_updater import UnitConversionUpdater


class LeftPanel(ctk.CTkFrame):
    def __init__(self, parent, right_panel_entries):
        super().__init__(parent)
        self._configure_grid()
        self._create_widgets()
        self.unit_updater = UnitConversionUpdater(right_panel_entries)

    def _configure_grid(self):
        """Configure the grid for the LeftPanel."""
        self.grid_columnconfigure(0, weight=1, uniform="A")
        self.grid_rowconfigure(tuple(range(11)), weight=1, uniform="A")

    def _create_widgets(self):
        """Create widgets for the LeftPanel."""
        self._create_label("Тип конвертации", LARGE_FONT)  # Title creation
        self._add_conversion_buttons()
        self._create_appearance_mode_optionmenu()

    def _create_label(self, text, font=SMALL_FONT, row=0, column=0, **grid_kwargs):
        """Create a label with given text, font, row, column and grid_kwargs."""
        ctk.CTkLabel(self, text=text, font=font).grid(
            row=row, column=column, **grid_kwargs
        )

    def _add_conversion_buttons(self):
        """Add buttons for each conversion type."""
        conversion_types = (
            "Температура",
            "Площадь",
            "Длина",
            "Объём",
            "Время",
            "Вес",
        )  # TODO: Remove hardcoded values in the code

        for row, conversion_type in enumerate(conversion_types, start=1):
            self._create_button(conversion_type, row)

    def _create_button(self, text, row):
        """Create a button with given text and row."""
        ctk.CTkButton(
            self,
            text=text,
            font=SMALL_FONT,
            command=lambda: self._button_event(text),
        ).grid(row=row, column=0, padx=20, pady=0)

    def _create_appearance_mode_optionmenu(self):
        """Create an option menu for appearance mode."""
        self._create_label("Внешний вид:", SMALL_FONT, row=9, pady=(0, 0))
        appearance_options = (
            "Светлый",
            "Тёмный",
            "Системный",
        )  # TODO: Remove hardcoded values in the code

        self.appearance_variable = ctk.StringVar(value=appearance_options[2])
        ctk.CTkOptionMenu(
            self,
            values=appearance_options,
            variable=self.appearance_variable,
            dropdown_font=SMALLEST_FONT,
            command=self._change_appearance_mode,
        ).grid(row=10, column=0, sticky="s", pady=(0, 10))

    def _change_appearance_mode(self, new_mode):
        """Change the appearance mode to the new_mode."""
        mode_mapping = {
            "Светлый": "Light",
            "Тёмный": "Dark",
            "Системный": "System",
        }  # TODO: Remove hardcoded values in the code
        ctk.set_appearance_mode(mode_mapping.get(new_mode, "System"))

    def _button_event(self, category_type):
        """Handle button event for the given category_type."""
        self.unit_updater.load_category_from_button(category_type)


class RightPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self._configure_grid()
        self.entries = self._create_entries()

    def _configure_grid(self):
        """Configures the grid for the RightPanel with specified weights and uniform."""
        self.grid_columnconfigure(0, weight=25, uniform="A")
        self.grid_columnconfigure(1, weight=5, uniform="A")
        self.grid_columnconfigure(2, weight=25, uniform="A")
        self.grid_columnconfigure(3, weight=5, uniform="A")
        self.grid_rowconfigure(tuple(range(8)), weight=1, uniform="A")

    def _create_entries(self):
        """Creates entries for the RightPanel and returns them as a list of tuples.
        Each tuple contains an entry, its symbol, its text, and its variable."""
        entries_list = [
            (self._create_entry(r, c)) for r in range(0, 16, 2) for c in [0, 2]
        ]
        return entries_list

    def _create_entry(self, row, column):
        """Creates a single entry at the given row and column, and returns it as a
        tuple with its symbol, text, and variable."""
        entry_var = ctk.StringVar()
        entry_text = self._create_label(row, column)
        entry = self._create_ctk_entry(row, column, entry_var)
        entry_symbol = self._create_symbol(row, column)
        return (entry, entry_symbol, entry_text, entry_var)

    def _create_label(self, row, column):
        """Creates a label at the given row and column, and returns it."""
        label = ctk.CTkLabel(
            self,
            text="",
            height=20,
            font=SMALLEST_FONT,
            text_color=("gray52", "gray62"),
        )
        label.grid(row=row, column=column, padx=(0, 5), pady=10, sticky="se")
        return label

    def _create_ctk_entry(self, row, column, entry_var):
        """Creates a CTkEntry at the given row and column, and returns it."""
        entry = ctk.CTkEntry(
            self, width=220, height=40, justify="right", textvariable=entry_var
        )
        entry.grid(row=row + 1, column=column, sticky="nse")
        return entry

    def _create_symbol(self, row, column):
        """Creates a symbol at the given row and column, and returns it."""
        symbol = ctk.CTkLabel(self, text="", font=SMALL_FONT, width=10)
        symbol.grid(row=row + 1, column=column + 1, sticky="w", padx=(5, 0))
        return symbol


class MainConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Converter")
        self._setup_ui()
        self.mainloop()

    def _setup_ui(self):
        """Setup the user interface by setting up the window, appearance and layout."""
        self._setup_window()
        self._setup_appearance()
        self._layout_panels()

    def _setup_window(self):
        """Setup the window with a specific geometry and make it non-resizable."""
        self.geometry("800x500")
        self.resizable(0, 0)

    def _setup_appearance(self):
        """Setup the appearance of the window with dark mode and a dark-blue theme."""
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

    def _layout_panels(self):
        """Configure the layout of panels with specific grid settings and positions."""
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.right_panel = RightPanel(self)
        self.right_panel.grid(row=0, column=1, padx=5, sticky="nsew")

        self.left_panel = LeftPanel(self, self.right_panel.entries)
        self.left_panel.grid(row=0, column=0, sticky="nsw")


if __name__ == "__main__":
    MainConverter()

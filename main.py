import customtkinter as ctk

from src.utils.unit_conversion_updater import UnitConversionUpdater
from src.utils.translator import Translator
from src.utils.ctk_separator import CTkWindowSeparator
from src.utils.widget_walker import walk_widgets
from src.utils.settings import (
    LARGE_FONT,
    SMALL_FONT,
    SMALLEST_FONT,
    APPEARANCE_MODE,
    COLOR_THEME,
)

# Constants for language translations
translator = Translator()
global _
_ = translator.gettext


class MainConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Converter")
        self._setup_ui()
        self.change_language_on_panels()
        self.mainloop()

    def _setup_ui(self):
        self._setup_window()
        self._setup_appearance()
        self._setup_panels()

    def _setup_window(self):
        self.geometry("800x500")
        self.resizable(0, 0)

    def _setup_appearance(self):
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)

    def _setup_panels(self):
        self.right_panel = RightPanel(self)
        self.settings_panel = SettingsPanel(self, self.change_language_on_panels)
        self.left_panel = LeftPanel(
            self,
            self.settings_panel,
            self.toggle_settings,
            self.right_panel.entries,
        )

        self._layout_panels()

    def _layout_panels(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.left_panel.grid(row=0, column=0, sticky="nsw")
        self.right_panel.grid(row=0, column=1, padx=5, sticky="nsew")
        self.settings_panel.grid(row=0, column=1, padx=5, sticky="nsew")
        self.settings_panel.grid_remove()

    def toggle_settings(self):
        if self.settings_panel.winfo_ismapped():
            self.settings_panel.grid_remove()
            self.right_panel.grid()
        else:
            self.right_panel.grid_remove()
            self.settings_panel.grid()

    def change_language_on_panels(self, lang_code=None):
        if lang_code is None:
            lang_code = self.settings_panel.current_lang.get()
        translator.change_language(lang_code)

        self.left_panel.update_ui()
        self.right_panel.update_ui()
        self.settings_panel.update_ui()


class LeftPanel(ctk.CTkScrollableFrame):
    CONVERSION_TYPES = [
        (_("Temperature")),
        (_("Area")),
        (_("Length")),
        (_("Volume")),
        (_("Time")),
        (_("Weight")),
        (_("Speed")),
        (_("Force")),
        (_("Fuel Consumption")),
        (_("Numeral System")),
        (_("Pressure")),
        (_("Energy")),
        (_("Power")),
        (_("Angles")),
        (_("Shoe size")),
        (_("Digital data")),
    ]

    def __init__(self, parent, setting_panel, setting_toggle, right_panel_entries):
        super().__init__(parent)
        self.setting_panel = setting_panel
        self.setting_toggle = setting_toggle
        self.unit_updater = UnitConversionUpdater(right_panel_entries)
        self._configure_grid()
        self._create_widgets()

    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _create_widgets(self):
        self._create_label("PyConverter", LARGE_FONT, pady=0)
        self._create_settings_button()
        self._add_conversion_buttons()

    def _create_label(self, text, font, **grid_kwargs):
        label = ctk.CTkLabel(self, text=text, font=font)
        label.grid(**grid_kwargs)

    def _create_settings_button(self):
        settings_button = ctk.CTkButton(
            self, text=_("Settings"), font=SMALL_FONT, command=self._open_settings
        )
        settings_button.grid(row=1, column=0, padx=0, pady=5)
        separator = CTkWindowSeparator(self, size=3, length=80, color="#878787")
        separator.grid(row=2, column=0, pady=0)

    def _add_conversion_buttons(self):
        for row, conversion_type in enumerate(self.CONVERSION_TYPES, start=3):
            self._create_button(row, conversion_type)

    def _create_button(self, row, text):
        button = ctk.CTkButton(
            self,
            text=text,
            font=SMALL_FONT,
            command=lambda t=text: self._button_event(t),
        )
        button.grid(row=row, column=0, padx=20, pady=3)

    def _button_event(self, category_type):
        if self.setting_panel.winfo_ismapped():
            self.setting_toggle()
        self.unit_updater.load_category_from_button(category_type)

    def _open_settings(self):
        self.setting_toggle()

    def update_ui(self):
        for widget in walk_widgets(self):
            if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton)):
                original_text = getattr(widget, "_original_text", None)
                if original_text is None:
                    original_text = widget.cget("text")
                    setattr(widget, "_original_text", original_text)
                widget.configure(text=_(original_text))


class SettingsPanel(ctk.CTkFrame):
    LANGUAGE_OPTIONS = (
        ("en", "English"),
        ("de", "German"),
        ("fr", "French"),
        ("es", "Spanish"),
        ("it", "Italian"),
        ("ru", "Russian"),
    )
    TRANSLATED_LANGUAGE_NAMES = {code: name for code, name in LANGUAGE_OPTIONS}
    APPEARANCE_OPTIONS = (_("Light"), (_("Dark")), (_("System")))

    def __init__(self, parent, change_language_method):
        super().__init__(parent)
        self.change_language = change_language_method

        self.current_lang = ctk.StringVar(value=self.LANGUAGE_OPTIONS[0][1])
        self.current_appearance = ctk.StringVar(value=self.APPEARANCE_OPTIONS[2])
        self.about_window = None
        self.configure(fg_color="transparent")
        self._configure_grid()
        self._create_widgets()

    def _configure_grid(self):
        self.grid_columnconfigure(0, uniform="B")
        self.grid_columnconfigure(1, uniform="B")
        self.grid_rowconfigure(tuple(range(5)), weight=0)

    def _create_widgets(self):
        self._create_settings_label()
        self._create_language_optionmenu()
        # self._crete_rm_trailing_zeros()  # TODO: Implement
        self._create_appearance_mode_optionmenu()
        self._create_about_button()

    def _create_settings_label(self):
        ctk.CTkLabel(
            self,
            text=(_("Settings")),
            font=LARGE_FONT,
        ).grid(row=0, column=0, sticky="nw", pady=(40, 0), padx=(20, 0))

    def _create_language_optionmenu(self):
        ctk.CTkLabel(
            self,
            text=(_("Language:")),
            font=SMALL_FONT,
        ).grid(row=1, column=0, sticky="nw", pady=(10, 0), padx=(20, 0))

        ctk.CTkOptionMenu(
            self,
            values=[_(name) for code, name in self.LANGUAGE_OPTIONS],
            variable=self.current_lang,
            dropdown_font=SMALLEST_FONT,
        ).grid(row=1, column=1, sticky="nw", pady=(5, 0), padx=(20, 0))

        self.current_lang.trace_add("write", self._on_language_change)

    def _on_language_change(self, *args):
        selected_lang_name = self.current_lang.get()
        self.TRANSLATED_LANGUAGE_NAMES = {
            code: _(name) for code, name in self.LANGUAGE_OPTIONS
        }
        for code, translated_name in self.TRANSLATED_LANGUAGE_NAMES.items():
            if translated_name == selected_lang_name:
                lang_code = code
                break
        self.change_language(lang_code)  # Change the language

    def update_ui(self):
        """Update the UI with the new language for the SettingsPanel."""
        for widget in walk_widgets(self):
            if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton)):
                original_text = getattr(widget, "_original_text", None)
                if original_text is None:
                    original_text = widget.cget("text")
                    setattr(widget, "_original_text", original_text)
                widget.configure(text=_(original_text))
            elif isinstance(widget, ctk.CTkOptionMenu):
                if widget.cget("variable") == self.current_lang:
                    translated_values = [
                        _(name) for code, name in self.LANGUAGE_OPTIONS
                    ]

                    # translated_variable = _(self.current_lang.get())
                    print("Original value:", self.current_lang.get())
                    # print("Translated value:", translated_variable)
                    widget.configure(values=tuple(translated_values))
                    # widget.set(translated_variable)
                elif widget.cget("variable") == self.current_appearance:
                    pass

    def _create_appearance_mode_optionmenu(self):
        """Create an option menu for appearance mode."""
        ctk.CTkLabel(self, text=_("Appearance:"), font=SMALL_FONT).grid(
            row=2, column=0, sticky="nw", pady=(10, 0), padx=(20, 0)
        )

        ctk.CTkOptionMenu(
            self,
            values=self.APPEARANCE_OPTIONS,
            variable=self.current_appearance,
            dropdown_font=SMALLEST_FONT,
            command=self._change_appearance_mode,
        ).grid(row=2, column=1, sticky="nw", pady=(5, 0), padx=(20, 0))

    def _change_appearance_mode(self, *args):
        new_mode = self.current_appearance.get()
        ctk.set_appearance_mode(new_mode)

    def _create_about_button(self):
        """Create an about button."""
        ctk.CTkButton(
            self,
            text=(_("About")),
            font=SMALL_FONT,
            command=self._open_about,
        ).grid(row=3, column=0, sticky="nw", pady=(10, 0), padx=(20, 0))

    def _open_about(self):
        if self.about_window is None or not self.about_window.winfo_exists():
            self.about_window = AboutWindow(self)
            self.about_window.transient(
                self
            )  # Make the About window transient to the main window
            self.about_window.grab_set()  # Set input focus to the About window
            self.about_window.lift()  # Bring the About window to the top
        else:
            self.about_window.lift()  # Bring the About window to the top if it already exists
            self.about_window.focus()  # Focus the About window if it already exists


class AboutWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("550x400")
        self.title(_("About"))
        self._configure_grid()
        self._create_content()

    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _create_content(self):
        info_label = ctk.CTkLabel(
            self, text=self._get_license_text(), wraplength=500, justify="left"
        )
        info_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def _get_license_text(self):
        license_text = (
            _(
                "MIT License\n\n"
                "Copyright (c) 2024 napHiwka\n\n"
                "Permission is hereby granted, free of charge, to any person obtaining a copy"
                'of this software and associated documentation files (the "Software"), to deal'
                "in the Software without restriction, including without limitation the rights"
                "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell"
                "copies of the Software, and to permit persons to whom the Software is"
                "furnished to do so, subject to the following conditions:\n\n"
                "The above copyright notice and this permission notice shall be included in all"
                "copies or substantial portions of the Software.\n\n"
                'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR'
                "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,"
                "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE"
                "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER"
                "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,"
                "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE"
                "SOFTWARE.\n\n"
            )
            + self._get_contact_info()
        )
        return license_text

    def _get_contact_info(self):
        return (
            _("For any inquiries or issues, please contact:\n") + "napHiwka@example.com"
        )


class RightPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self._configure_grid()
        self.entries = self._create_entries()

    def _configure_grid(self):
        """Configures the grid for the RightPanel with specified weights and uniform."""
        self.grid_columnconfigure(0, weight=25, uniform="C")
        self.grid_columnconfigure(1, weight=5, uniform="C")
        self.grid_columnconfigure(2, weight=25, uniform="C")
        self.grid_columnconfigure(3, weight=5, uniform="C")
        self.grid_rowconfigure(tuple(range(8)), weight=1, uniform="C")

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

    def update_ui(self):
        """Update the UI with the new language for the RightPanel."""
        for widget in walk_widgets(self):
            if isinstance(widget, ctk.CTkLabel):
                original_text = getattr(widget, "_original_text", None)
                if original_text:
                    if original_text is None:
                        original_text = widget.cget("text")
                        setattr(widget, "_original_text", original_text)
                    widget.configure(text=_(original_text))


if __name__ == "__main__":
    MainConverter()
